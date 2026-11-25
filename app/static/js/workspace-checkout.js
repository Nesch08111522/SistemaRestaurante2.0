import {requestJSON,message} from './workspace-api.js';
const form=document.getElementById('checkout-form');
if(form){
  const status=document.getElementById('checkout-status'), inputs=[...form.querySelectorAll('[data-dish]')];
  let key=crypto.randomUUID(),busy=false;
  const totalCents=()=>inputs.reduce((sum,n)=>sum+Math.round(Number(n.dataset.price)*100)*Number(n.value||0),0);
  form.addEventListener('input',()=>{if(!busy)key=crypto.randomUUID();document.getElementById('checkout-total').textContent=new Intl.NumberFormat('es-PE',{style:'currency',currency:'PEN'}).format(totalCents()/100);});
  form.addEventListener('submit',async event=>{
    event.preventDefault();if(busy||!form.reportValidity())return;
    const items=inputs.filter(n=>Number(n.value)>0).map(n=>({dish_id:Number(n.dataset.dish),quantity:Number(n.value)}));
    if(!items.length){message(status,'Selecciona al menos un plato.',true);return;}
    busy=true;const button=form.querySelector('[type="submit"]');button.disabled=true;
    message(status,'Confirmando el pedido…');
    try{
      const result=await requestJSON(form.dataset.endpoint,{method:'POST',body:{restaurant_id:Number(form.dataset.restaurant),items,channel:document.getElementById('checkout-channel').value,request_key:key,expected_total:(totalCents()/100).toFixed(2)}});
      location.assign(result.url);
    }catch(error){message(status,error.message+' Si hubo un problema de conexión, puedes reintentar sin cambiar el pedido.',true);}
    finally{busy=false;button.disabled=false;}
  });
}
