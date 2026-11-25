// Optional real-browser suite. Requires @playwright/test in a development environment.
// Start python -m tests.e2e.menu3d_fixture first; NEVER point at production.
const {test,expect}=require('@playwright/test');
const origin='http://127.0.0.1:5093';
for(const width of [360,768,1440]){
  test(`public menu responsive and functional at ${width}px`,async({page})=>{
    await page.setViewportSize({width,height:900});
    await page.goto(origin+'/ar/restaurantes/1');
    await expect(page.locator('#m3d-grid .m3d-card')).toHaveCount(4);
    expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
    await page.getByRole('searchbox',{name:'Buscar un plato'}).fill('prueba 2');
    await expect(page.locator('#m3d-grid .m3d-card')).toHaveCount(1);
    await page.locator('#m3d-grid').getByRole('button',{name:'Ver detalles'}).click();
    await expect(page.getByRole('dialog')).toBeVisible();
    await expect(page.locator('#m3d-viewer-status')).toContainText('todavía no disponible');
    await page.keyboard.press('Escape');await expect(page.getByRole('dialog')).not.toBeVisible();
  });
}
test('3D is lazy, loads on demand, and exposes camera controls',async({page})=>{
  const models=[];page.on('request',r=>{if(r.url().includes('qa-test-model'))models.push(r.url());});
  await page.goto(origin+'/ar/restaurantes/1');await expect(page.locator('#m3d-grid .m3d-card')).toHaveCount(4);
  expect(models).toHaveLength(0);
  await page.locator('#m3d-grid').getByRole('button',{name:'Explorar en 3D'}).click();
  await expect(page.locator('#m3d-controls')).toBeVisible({timeout:45000});
  expect(models.length).toBeGreaterThan(0);
  await page.getByRole('button',{name:'Giro automático'}).click();
  await expect(page.getByRole('button',{name:'Giro automático'})).toHaveAttribute('aria-pressed','true');
});
test('administration offers editor and studio on mobile',async({page})=>{
  await page.setViewportSize({width:360,height:900});await page.goto(origin+'/ar/gestion');
  await expect(page.locator('#m3d-admin-grid .m3d-card')).toHaveCount(4);
  await page.getByRole('button',{name:'Registrar plato'}).click();
  await expect(page.locator('#m3d-editor')).toBeVisible();await page.keyboard.press('Escape');
  await page.getByRole('button',{name:'Fotos y modelos'}).first().click();
  await expect(page.locator('#m3d-studio')).toBeVisible();
  await expect(page.locator('#m3d-photo-form input[type=file]')).toHaveAttribute('multiple','');
});
