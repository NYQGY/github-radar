let data,view='all';
const $=id=>document.getElementById(id);
const fmt=n=>new Intl.NumberFormat('zh-CN').format(n);
function el(tag,text,cls){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e}
function render(){
 let rows=view==='archive'?(data.reports.find(r=>r.date===$('report').value)?.projects||[]):view==='weekly'?data.weekly:data.projects;
 const q=$('search').value.toLowerCase().trim();
 rows=rows.filter(p=>(!$('language').value||p.language===$('language').value)&&[p.name,p.description,...p.topics].join(' ').toLowerCase().includes(q));
 if(view==='all')rows=[...rows].sort((a,b)=>$('sort').value==='recent'?new Date(b.created)-new Date(a.created):b.stars-a.stars);
 $('note').textContent=view==='weekly'?'GitHub Trending 周榜中，按本周获得的 Star 数排名的 Top 10。':view==='archive'?'每周一保存当时的 GitHub Trending 周榜。':`找到 ${rows.length} 个项目 · 采集热门、近期及 AI 项目；简介保留 GitHub 原文。`;
 $('projects').replaceChildren();
 if(!rows.length)$('projects').append(el('div',view==='all'?'没有匹配的项目，试试其他关键词。':'没有匹配的项目。','empty'));
 rows.forEach((p,i)=>{const card=el('article',undefined,'card');const top=el('div',undefined,'top');top.append(el('span',String(i+1).padStart(2,'0')),el('span',p.language));const h=el('h2');const a=el('a',p.name);a.href=p.url;a.target='_blank';a.rel='noopener noreferrer';h.append(a);const metrics=el('div',undefined,'metrics');metrics.append(el('span','☆ '+fmt(p.stars)),el('span',p.weekly_stars!==undefined?'本周 +'+fmt(p.weekly_stars):'创建于 '+new Date(p.created).toLocaleDateString('zh-CN',{timeZone:'Asia/Shanghai'}),'growth'));card.append(top,h,el('p',p.description),el('div',p.topics.slice(0,3).join(' / '),'tags'),metrics);$('projects').append(card)});
}
fetch('data.json').then(r=>{if(!r.ok)throw Error();return r.json()}).then(d=>{data=d;$('count').textContent=fmt(d.projects.length);$('ready').textContent=fmt(d.weekly.length);$('date').textContent=new Date(d.updated).toLocaleDateString('zh-CN',{timeZone:'Asia/Shanghai'});[...new Set(d.projects.map(p=>p.language))].sort().forEach(l=>{const o=el('option',l);o.value=l;$('language').append(o)});[...d.reports].reverse().forEach(r=>{const o=el('option',r.date);o.value=r.date;$('report').append(o)});render()}).catch(()=>{$('note').textContent='数据加载失败，请刷新重试。'});
['search','language','sort','report'].forEach(id=>$(id).addEventListener(id==='search'?'input':'change',()=>data&&render()));
document.querySelectorAll('nav button').forEach(b=>b.onclick=()=>{view=b.dataset.view;document.querySelectorAll('nav button').forEach(x=>x.classList.toggle('active',x===b));$('report').hidden=view!=='archive';$('sort').hidden=view!=='all';if(data)render()});
