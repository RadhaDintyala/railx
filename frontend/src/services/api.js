const API=import.meta.env.VITE_API_URL||'http://localhost:8000';
export const tokenKey='irctsToken';
async function request(path,options={}){const headers={'Content-Type':'application/json',...(options.headers||{})};const token=localStorage.getItem(tokenKey);if(token)headers.Authorization=`Bearer ${token}`;const r=await fetch(API+path,{...options,headers});const d=await r.json();if(r.status===401){window.dispatchEvent(new Event('auth:invalid'));throw Error(d.error||'Your session has expired.');}if(!r.ok)throw Error(d.error||'Something went wrong');return d}
export const signup=(body)=>request('/api/auth/signup',{method:'POST',body:JSON.stringify(body)});
export const login=(body)=>request('/api/auth/login',{method:'POST',body:JSON.stringify(body)});
export const currentUser=()=>request('/api/auth/me');
export const searchTrains=(q)=>{const params=new URLSearchParams();Object.entries(q).forEach(([key,value])=>{if(value!==undefined&&value!==''&&value!==null)params.set(key,value)});return request(`/api/trains/search?${params}`)};
export const searchStations=(q='')=>request(`/api/stations/search?q=${encodeURIComponent(q)}`);
export const transportOptions=(q)=>{const params=new URLSearchParams(q);return request(`/api/transport/options?${params}`)};
export const planJourney=(body)=>request('/api/journey/plan',{method:'POST',body:JSON.stringify(body)});
