/* Fluxo de navegador somente em projeto Compose isolado de verificação. */
const {chromium} = require('playwright');
const {AxeBuilder} = require('@axe-core/playwright');
const {execFileSync} = require('node:child_process');
const fs = require('node:fs');
const assert = require('node:assert/strict');
const project = process.env.CHECK_COMPOSE_PROJECT;
if (!project || !project.includes('check')) throw new Error('Use um projeto isolado com check no nome.');
const base = process.env.CHECK_BASE_URL || 'http://localhost:8082';
const out = 'artifacts/sprint-2';
fs.mkdirSync(out,{recursive:true});
const compose = args => execFileSync('docker',['compose','-p',project,'exec','-T','app',...args],{encoding:'utf8'});
const credentials=JSON.parse(compose(['python','-c',"from pathlib import Path; print(Path('/data/demo-credentials.json').read_text())"]));
(async()=>{
  const browser=await chromium.launch({headless:true});
  try {
    const context=await browser.newContext({viewport:{width:1440,height:1000}});
    const page=await context.newPage(); const errors=[]; const audited=[];
    page.on('pageerror',e=>errors.push(e.message));
    async function login(role,email=null,password=null){
      await page.goto(base+'/login');
      await page.getByLabel('E-mail',{exact:true}).fill(email || role+'@example.com');
      await page.getByLabel('Senha',{exact:true}).fill(password || credentials[role+'@example.com']);
      await page.getByRole('button',{name:'Entrar',exact:true}).click();
      await page.waitForURL(base+'/');
    }
    async function logout(){await page.getByRole('button',{name:'Sair',exact:true}).click();}
    async function inspect(name){
      const result=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();
      assert.deepEqual(result.violations.map(v=>v.id),[],'axe: '+name);
      for(const width of [1440,768,390,320]){
        await page.setViewportSize({width,height:1000});
        assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Overflow '+name+' '+width);
        if(width===1440 || width===390) await page.screenshot({path:`${out}/${name}-${width}.png`,fullPage:true});
      }
      await page.setViewportSize({width:1440,height:1000}); audited.push(name);
    }
    if(process.argv.includes('--verify-persistence')){
      const state=JSON.parse(fs.readFileSync(out+'/state.json','utf8'));
      await login('tecnico'); await page.goto(base+state.path);
      await page.getByRole('heading',{name:'Solução',exact:true}).waitFor();
      assert((await page.locator('.description').last().textContent()).includes('Correção de rede aplicada'));
      const persisted=JSON.parse(compose(['python','-c',"import json;from helpdesk import create_app;from helpdesk.models import db,Ticket,StatusEvent;app=create_app();\nwith app.app_context():\n t=db.session.get(Ticket,'"+state.id+"');print(json.dumps([t.status,t.priority,t.solution,str(t.completed_at),db.session.query(StatusEvent).filter_by(ticket_id=t.id).count()]))"]));
      assert.equal(persisted[0],'Concluído');assert.equal(persisted[1],'Alta');assert.equal(persisted[4],2);
      await page.goto(base+'/kanban');assert.equal(await page.locator('#S2-04 select').inputValue(),'Em andamento');
      await page.locator('#S2-04 select').selectOption(state.column);await page.locator('#S2-04 button').click();
      console.log('Persistência após recriação: chamado concluído, solução, prioridade, dois eventos, credenciais e coluna do Kanban preservados.');
    } else {
      await page.goto(base+'/login');await page.keyboard.press('Tab');
      assert.equal(await page.evaluate(()=>document.activeElement.textContent),'Pular para o conteúdo');
      await login('solicitante');await page.goto(base+'/chamados');await inspect('lista-vazia');
      await page.goto(base+'/chamados/novo');
      await page.getByLabel('Título',{exact:true}).fill('Problema de rede para demonstração');
      await page.getByLabel('Categoria',{exact:true}).selectOption('Rede');
      await page.getByLabel('Descrição',{exact:true}).fill('Equipamento de teste não acessa a rede.');
      await page.getByRole('button',{name:'Enviar chamado',exact:true}).click();
      await page.waitForURL(/\/chamados\/[0-9a-f-]+$/);
      await page.getByRole('link',{name:'Acompanhar este chamado',exact:true}).click();
      const path=new URL(page.url()).pathname;const id=path.split('/')[2];await inspect('detalhe-solicitante');
      compose(['python','-c',"from helpdesk import create_app;from helpdesk.models import db,Ticket,User;app=create_app();\nwith app.app_context():\n u=db.session.scalar(db.select(User).where(User.email=='solicitante@example.com'));\n for i in range(12): db.session.add(Ticket(requester_id=u.id,title=f'Consulta de rede {i:02}',category='Rede',description='Dados sintéticos para verificar paginação.'))\n v=User(name='Solicitante de isolamento',email='isolamento@example.com',role='solicitante');v.set_password('test-password');db.session.add(v);db.session.commit()"]);
      await page.goto(base+'/chamados?status=Aberto&category=Rede');await inspect('lista-filtrada');
      assert.equal(await page.locator('.ticket-row').count(),10);
      await page.getByRole('link',{name:'Próxima',exact:true}).click();assert.equal(await page.locator('.ticket-row').count(),3);
      assert(new URL(page.url()).searchParams.get('category')==='Rede');
      await page.goto(base+'/chamados?status=Concluído&category=Software');await inspect('busca-vazia');
      await page.goto(base+'/chamados?category=Inexistente');await inspect('filtro-invalido');
      await logout();await login('tecnico');await page.goto(base+path);await inspect('detalhe-tecnico');
      await page.getByLabel('Prioridade',{exact:true}).selectOption('Alta');await page.getByRole('button',{name:'Salvar prioridade',exact:true}).click();
      await page.getByRole('button',{name:'Iniciar atendimento',exact:true}).click();await inspect('atendimento');
      await page.getByLabel('Solução',{exact:true}).fill('   ');await page.getByRole('button',{name:'Concluir chamado',exact:true}).click();
      assert((await page.locator('[role=alert]').textContent()).includes('não foi salva'));
      await inspect('solucao-invalida');
      await page.getByLabel('Solução',{exact:true}).fill('Correção de rede aplicada. <script>texto sem execução</script>');
      await page.getByRole('button',{name:'Concluir chamado',exact:true}).click();await inspect('concluido');
      assert.equal(await page.locator('script').count(),0);assert.equal(await page.getByRole('button',{name:'Salvar prioridade'}).count(),0);
      await page.goto(base+'/kanban');const column=await page.locator('#S2-04 select').inputValue();
      await page.locator('#S2-04 select').selectOption('Em andamento');await page.locator('#S2-04 button').click();
      fs.writeFileSync(out+'/state.json',JSON.stringify({path,id,column}),{mode:0o600});
      await logout();await login('solicitante');await page.goto(base+path);await inspect('concluido-solicitante');
      assert.equal(await page.getByRole('button',{name:'Concluir chamado'}).count(),0);
      await logout();await login('solicitante','isolamento@example.com','test-password');
      const forbidden=await page.goto(base+path);assert.equal(forbidden.status(),404);
      await page.goto(base+'/chamados');assert.equal(await page.locator('.ticket-row').count(),0);
      assert.deepEqual(errors,[]);
      console.log('Fluxos completos, filtros combinados, paginação, isolamento e atendimento aprovados. '+audited.length+' páginas/estados sem violações axe nos escopos executados e sem overflow em 320/390/768/1440px.');
    }
  } finally {await browser.close();}
})().catch(error=>{console.error(error);process.exit(1);});
