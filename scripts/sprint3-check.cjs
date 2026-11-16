/* Fluxos com dados sintéticos somente em projeto Compose isolado. */
const {chromium}=require('playwright');
const {AxeBuilder}=require('@axe-core/playwright');
const {execFileSync}=require('node:child_process');
const fs=require('node:fs');
const assert=require('node:assert/strict');
const project=process.env.CHECK_COMPOSE_PROJECT;
if(!project || !project.includes('check')) throw Error('Use projeto isolado com check no nome.');
const base=process.env.CHECK_BASE_URL || 'http://localhost:8083';
const out='artifacts/sprint-3';fs.mkdirSync(out,{recursive:true});
const compose=args=>execFileSync('docker',['compose','-p',project,'exec','-T','app',...args],{encoding:'utf8'});
// Recuperar credenciais em memória; nunca escrever seus valores nos logs ou artefatos.
const credentials=JSON.parse(compose(['python','-c',"from pathlib import Path;print(Path('/data/demo-credentials.json').read_text())"]));
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
  const context=await browser.newContext({viewport:{width:1440,height:1000}});
  const page=await context.newPage();const errors=[];const audited=[];
  page.on('pageerror',e=>errors.push(e.message));
  async function login(role,email,password){
   await page.goto(base+'/login');
   await page.getByLabel('E-mail',{exact:true}).fill(email||role+'@example.com');
   await page.getByLabel('Senha',{exact:true}).fill(password||credentials[role+'@example.com']);
   await page.getByRole('button',{name:'Entrar',exact:true}).click();await page.waitForURL(base+'/');
  }
  async function logout(){await page.getByRole('button',{name:'Sair',exact:true}).click();}
  async function inspect(name){
   const audit=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();
   assert.deepEqual(audit.violations.map(v=>v.id),[],'axe: '+name);
   for(const width of [1440,768,390,320]){
    await page.setViewportSize({width,height:1000});
    assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Overflow '+name+' '+width);
    if(width===1440||width===390) await page.screenshot({path:`${out}/${name}-${width}.png`,fullPage:true});
   }
   await page.setViewportSize({width:1440,height:1000});audited.push(name);
  }
  async function assertCounts(status,priority){
   for(const [group,expected] of [[0,status],[1,priority]]){
    const actual=await page.locator('.indicator-table').nth(group).locator('tbody td').allTextContents();
    assert.deepEqual(actual.map(x=>Number(x)),expected);
   }
  }
  if(process.argv.includes('--verify-persistence')){
   const state=JSON.parse(fs.readFileSync(out+'/state.json','utf8'));
   await login('tecnico');await page.goto(base+state.path);
   assert.equal(await page.title(),'Detalhes do chamado · Suporte de TI');
   assert.equal(await page.locator('.timeline li').count(),5);
   assert((await page.locator('.timeline').textContent()).includes('Observação após conclusão'));
   assert.equal(await page.getByRole('button',{name:'Salvar prioridade'}).count(),0);
   await page.goto(base+'/indicadores');await assertCounts([0,0,1],[0,0,1]);
   await page.goto(base+'/kanban');assert.equal(await page.locator('#S3-04 select').inputValue(),'Em andamento');
   await page.locator('#S3-04 select').selectOption(state.column);await page.locator('#S3-04 button').click();
   console.log('Persistência confirmada: chamado, solução, prioridade, três anotações, dois eventos, credenciais e coluna do Kanban preservados.');
  }else{
   await page.goto(base+'/login');await page.keyboard.press('Tab');
   assert.equal(await page.evaluate(()=>document.activeElement.textContent),'Pular para o conteúdo');
   await login('tecnico');await page.goto(base+'/indicadores');await assertCounts([0,0,0],[0,0,0]);await inspect('indicadores-vazios');
   await logout();await login('solicitante');
   await page.getByRole('link',{name:'Abrir chamado',exact:true}).first().click();
   await page.getByLabel('Título',{exact:true}).fill('Verificação sintética de rede da Sprint 3');
   await page.getByLabel('Descrição',{exact:true}).fill('Equipamento de ensaio não acessa a rede local.');
   await page.getByLabel('Categoria',{exact:true}).selectOption('Rede');
   await page.getByRole('button',{name:'Enviar chamado',exact:true}).click();await page.waitForURL(/\/chamados\/[0-9a-f-]+$/);
   await page.getByRole('link',{name:'Acompanhar este chamado',exact:true}).click();
   const path=new URL(page.url()).pathname;const id=path.split('/')[2];
   assert((await page.locator('#historico').textContent()).includes('Ainda não há registros'));
   await inspect('historico-vazio-solicitante');
   assert.equal((await page.goto(base+'/indicadores')).status(),403);
   await logout();await login('tecnico');await page.goto(base+'/indicadores');await assertCounts([1,0,0],[0,1,0]);
   await page.goto(base+path);await inspect('historico-vazio-tecnico');
   await page.getByLabel('Anotação de atendimento',{exact:true}).fill('   ');
   await page.getByRole('button',{name:'Registrar anotação',exact:true}).click();
   assert((await page.locator('[role=alert]').textContent()).includes('não foi salva'));await inspect('anotacao-invalida');
   await page.getByLabel('Anotação de atendimento',{exact:true}).fill('Primeira análise. <script>texto sem execução</script>');
   await page.getByRole('button',{name:'Registrar anotação',exact:true}).click();
   assert.equal(await page.locator('.timeline li').count(),1);assert.equal(await page.locator('script').count(),0);
   await page.reload();assert.equal(await page.locator('.timeline li').count(),1);
   await page.getByLabel('Prioridade',{exact:true}).selectOption('Alta');await page.getByRole('button',{name:'Salvar prioridade',exact:true}).click();
   await page.getByRole('button',{name:'Iniciar atendimento',exact:true}).click();
   await page.getByLabel('Anotação de atendimento',{exact:true}).fill('Conexão testada; identificada configuração incorreta.');
   await page.getByRole('button',{name:'Registrar anotação',exact:true}).click();await inspect('historico-em-atendimento');
   await page.getByLabel('Solução',{exact:true}).fill('Configuração corrigida e conexão validada.');
   await page.getByRole('button',{name:'Concluir chamado',exact:true}).click();
   await page.getByLabel('Anotação de atendimento',{exact:true}).fill('Observação após conclusão: solicitante orientado.');
   await page.getByRole('button',{name:'Registrar anotação',exact:true}).click();
   assert.equal(await page.locator('.timeline li').count(),5);assert.equal(await page.getByRole('button',{name:'Iniciar atendimento'}).count(),0);
   await inspect('historico-concluido-tecnico');
   await page.goto(base+'/indicadores');await assertCounts([0,0,1],[0,0,1]);await inspect('indicadores-preenchidos');
   await page.goto(base+'/kanban');const column=await page.locator('#S3-04 select').inputValue();
   await page.locator('#S3-04 select').selectOption('Em andamento');await page.locator('#S3-04 button').click();
   fs.writeFileSync(out+'/state.json',JSON.stringify({path,id,column}),{mode:0o600});
   await logout();await login('solicitante');await page.goto(base+path);await inspect('historico-concluido-solicitante');
   assert.equal(await page.locator('.timeline li').count(),5);assert.equal(await page.getByRole('button',{name:'Registrar anotação'}).count(),0);
   const token=await page.locator('input[name=csrf_token]').first().inputValue();
   assert.equal((await page.request.post(base+'/chamados/'+id+'/anotacoes',{form:{content:'Escrita proibida',csrf_token:token}})).status(),403);
   compose(['python','-c',"from helpdesk import create_app;from helpdesk.models import db,User;app=create_app();\nwith app.app_context():\n u=User(name='Solicitante de isolamento',email='isolamento@example.com',role='solicitante');u.set_password('test-password');db.session.add(u);db.session.commit()"]);
   await logout();await login('solicitante','isolamento@example.com','test-password');
   assert.equal((await page.goto(base+path)).status(),404);
   assert.deepEqual(errors,[]);
   console.log('RF01 a RF06 verificados nos dois perfis; '+audited.length+' estados sem violações axe nos escopos executados e sem overflow em 320/390/768/1440px.');
  }
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
