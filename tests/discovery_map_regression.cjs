const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const root = process.env.RESTAURANT_ROOT || process.cwd();
const html = fs.readFileSync(path.join(root, 'app/templates/discovery/index.html'), 'utf8');
const numeric = html.slice(html.indexOf('    function numeric('), html.indexOf('    function formatPrice('));
const source = html.slice(html.indexOf('    let discoveryMap;'), html.indexOf('    async function loadMapPoints()'));
function setup() {
  const markers = new Set();
  const controls = ['zoom-in', 'zoom-out', 'reset'].map(action => ({dataset:{mapAction:action}, addEventListener(_, fn){this.click=fn;}}));
  let resizeCallback;
  class MapMock {
    constructor(){this.resizes=0; this.fits=[];}
    addControl(){} resize(){this.resizes++;} setStyle(){}
    fitBounds(bounds){this.fits.push(bounds.points);}
    zoomIn(){} zoomOut(){}
  }
  class Marker {
    constructor(options){this.element=options.element;}
    setLngLat(coords){this.coords=coords; return this;}
    addTo(map){this.map=map; markers.add(this); return this;}
    remove(){markers.delete(this);}
  }
  class Bounds {
    constructor(){this.points=[];}
    extend(coords){this.points.push(coords);return this;}
    isEmpty(){return this.points.length===0;}
  }
  const maplibregl = {Map:MapMock, Marker, LngLatBounds:Bounds, NavigationControl:class{}};
  const context = vm.createContext({window:{maplibregl}, maplibregl,
    el:{mapCount:{}},
    document:{documentElement:{dataset:{theme:'light'}}, getElementById:()=>({}), querySelectorAll:()=>controls,
      createElement:()=>({setAttribute(){}, addEventListener(){}, appendChild(){}})},
    ResizeObserver:class{constructor(fn){resizeCallback=fn;}observe(){}},
    MutationObserver:class{observe(){}}
  });
  vm.runInContext(numeric + source + ';globalThis.getMap=()=>discoveryMap;',context);
  return {context, markers, controls, resize:()=>resizeCallback()};
}
const trujillo = {id:1, lat:-8.1116, lng:-79.0287};
const lima = {id:2, lat:-12.0464, lng:-77.0428};
test('repeated API renders replace markers without errors or duplicates',()=>{
  const {context,markers}=setup();
  context.renderDiscoveryMap([trujillo,lima]);
  context.renderDiscoveryMap([trujillo,lima]);
  assert.equal(markers.size,2);
  assert.deepEqual(Array.from(markers, m=>Array.from(m.coords)),[[-79.0287,-8.1116],[-77.0428,-12.0464]]);
});
test('filtered city points determine reset bounds; empty results keep the current view',()=>{
  const {context,markers,controls}=setup();
  context.renderDiscoveryMap([trujillo,lima]);
  context.renderDiscoveryMap([lima]);
  controls[2].click();
  assert.equal(markers.size,1);
  assert.deepEqual(Array.from(context.getMap().fits.at(-1),p=>Array.from(p)),[[-77.0428,-12.0464]]);
  context.renderDiscoveryMap([]);
  const fits=context.getMap().fits.length;
  controls[2].click();
  assert.equal(context.getMap().fits.length,fits);
  assert.equal(markers.size,0);
});
test('missing and out-of-range coordinates do not become false map locations',()=>{
  const {context,markers}=setup();
  context.renderDiscoveryMap([trujillo, ...[null,undefined,'',NaN,91,-91].map(lat=>({lat,lng:-79})),{lat:-8,lng:181}]);
  assert.equal(markers.size,1);
  assert.match(context.el.mapCount.textContent,/^1 ubicaciones/);
});
test('container resize updates map dimensions without changing marker coordinates',()=>{
  const {context,markers,resize}=setup();
  context.renderDiscoveryMap([trujillo]);
  const before=context.getMap().resizes;
  resize();
  assert.equal(context.getMap().resizes,before+1);
  assert.deepEqual(Array.from([...markers][0].coords),[-79.0287,-8.1116]);
});
