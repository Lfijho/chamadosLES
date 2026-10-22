/* Verificação opcional com Playwright e axe, somente em projeto Compose de teste. */
const { chromium } = require('playwright');
const { AxeBuilder } = require('@axe-core/playwright');
const { execFileSync } = require('node:child_process');
const fs = require('node:fs');
const assert = require('node:assert/strict');

(async () => {
  const project = process.env.CHECK_COMPOSE_PROJECT;
  if (!project || !project.includes('check')) throw new Error('Defina CHECK_COMPOSE_PROJECT com um projeto isolado contendo check no nome.');
  const base = process.env.CHECK_BASE_URL || 'http://localhost:8080';
  const out = 'artifacts/browser';
  fs.mkdirSync(out, {recursive:true});
  const credentials = JSON.parse(execFileSync('docker', ['compose', '-p', project, 'exec', '-T', 'app',
    'python', '-c', "from pathlib import Path; print(Path('/data/demo-credentials.json').read_text())"], {encoding:'utf8'}));
  const statePath = process.env.CHECK_STATE_FILE || '/tmp/helpdesk-browser-check-state.json';
  const browser = await chromium.launch({headless:true});
  const errors = [];
  const context = await browser.newContext({viewport:{width:1440,height:1000}});
  const page = await context.newPage();
  page.on('pageerror', error => errors.push(error.message));
  async function login(role) {
    await page.goto(base + '/login');
    await page.getByLabel('E-mail', {exact:true}).fill(role + '@example.com');
    await page.getByLabel('Senha', {exact:true}).fill(credentials[role + '@example.com']);
    await page.getByRole('button', {name:'Entrar', exact:true}).click();
    await page.waitForURL(base + '/');
  }
  const audited = [];
  async function inspect(name) {
    const result = await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();
    if(result.violations.length) throw new Error(JSON.stringify(result.violations.map(v=>({id:v.id, nodes:v.nodes.map(n=>n.target)}))));
    for (const width of [1440,768,390,320]) {
      await page.setViewportSize({width,height:1000});
      assert(await page.evaluate(()=>document.documentElement.scrollWidth <= innerWidth), 'Overflow: ' + name + ' ' + width);
      if(width===1440 || width===390) await page.screenshot({path:`${out}/${name}-${width===1440?'desktop':'mobile'}.png`, fullPage:true});
    }
    await page.setViewportSize({width:1440,height:1000});
    audited.push(name);
  }
  if(process.argv.includes('--verify-persistence')) {
    const state = JSON.parse(fs.readFileSync(statePath, 'utf8'));
    await context.addCookies(state.cookies);
    await page.goto(base + state.ticketPath);
    assert.equal(await page.getByRole('heading', {name:'Verificação de persistência'}).count(),1);
    await page.getByRole('button', {name:'Sair', exact:true}).click();
    await login('tecnico');
    await page.goto(base+'/kanban');
    assert.equal(await page.locator('#S1-04 select').inputValue(), 'A fazer');
    await page.locator('#S1-04 select').selectOption(state.originalColumn);
    await page.locator('#S1-04 button').click();
    console.log('Persistência confirmada: chamado, sessão, credenciais e coluna Kanban após recriação. Coluna original restaurada.');
  } else {
    await page.goto(base+'/login');
    await page.keyboard.press('Tab');
    assert.equal(await page.evaluate(()=>document.activeElement.textContent), 'Pular para o conteúdo');
    await inspect('login');
    await login('solicitante');
    await inspect('home');
    await page.getByRole('link',{name:'Abrir chamado',exact:true}).last().click();
    await inspect('new-ticket');
    await page.getByLabel('Título', {exact:true}).fill('Verificação de persistência');
    await page.getByLabel('Categoria', {exact:true}).selectOption('Rede');
    await page.getByLabel('Descrição', {exact:true}).fill('Dados sintéticos para verificar a persistência após recriar o container.');
    await page.getByRole('button',{name:'Enviar chamado'}).click();
    await page.waitForURL(/\/chamados\/[0-9a-f-]+$/);
    const ticketPath = new URL(page.url()).pathname;
    await inspect('confirmation');
    await page.reload();
    assert.equal(await page.getByText('Chamado registrado com sucesso.').count(),1);
    await page.getByRole('button',{name:'Sair',exact:true}).click();
    await page.goto(base+ticketPath);
    assert(new URL(page.url()).pathname==='/login');
    await login('tecnico');
    await inspect('technician');
    await page.getByRole('link',{name:'Quadro do projeto',exact:true}).click();
    await inspect('kanban');
    const originalColumn = await page.locator('#S1-04 select').inputValue();
    await page.locator('#S1-04 select').selectOption('A fazer');
    await page.locator('#S1-04 button').click();
    // Uma sessão de solicitante nova precisa permanecer válida através da recriação.
    await page.getByRole('button',{name:'Sair',exact:true}).click();
    await login('solicitante');
    const activeCookies = await context.cookies();
    fs.writeFileSync(statePath, JSON.stringify({ticketPath, cookies:activeCookies, originalColumn}), {mode:0o600});
    assert.equal(errors.length,0);
    console.log('Navegador: login dos dois perfis, abertura, PRG, logout, Kanban; axe sem violações nas páginas: '+audited.join(', ')+'. Sem overflow em 320/390/768/1440 px.');
  }
  await browser.close();
})().catch(error=>{ console.error(error);process.exit(1); });
