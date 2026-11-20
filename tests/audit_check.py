# Аудит «Гипно-стройности»: безопасность голодания, решения по методике, данные.
# Запуск: python3 tests/audit_check.py index.html
import asyncio,sys,os,shutil,tempfile,http.server,threading,functools,json
from playwright.async_api import async_playwright
H=os.path.abspath(sys.argv[1]);tmp=tempfile.mkdtemp();shutil.copy(H,tmp+'/index.html');os.symlink(os.path.dirname(H)+'/media',tmp+'/media');open(tmp+'/blank.html','w').write('<!doctype html><title>b</title>')
srv=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(type('Q',(http.server.SimpleHTTPRequestHandler,),{'log_message':lambda *a:None}),directory=tmp));threading.Thread(target=srv.serve_forever,daemon=True).start()
URL=f'http://127.0.0.1:{srv.server_address[1]}/index.html'
R=[]
def ok(n,c,x=''):R.append(bool(c));print(('PASS ' if c else 'FAIL ')+n+(' · '+str(x) if x!='' else ''))
# профиль: сегодня — пятница 2-й недели (день 12)
SETUP="""(dayToday)=>{const t=new Date();t.setHours(0,0,0,0);const st=new Date(t);st.setDate(st.getDate()-(dayToday-1));const iso=d=>d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');
  localStorage.clear();localStorage.setItem('gipno_v1',JSON.stringify({days:{},weeks:{},final:{},profile:{name:'Тест',prep:iso(st),start:iso(st),sex:'m',height:'180',wake:'06:30',w0:'95',created:1}}));}"""
async def m():
  async with async_playwright() as p:
    b=await p.chromium.launch();ctx=await b.new_context(timezone_id='Asia/Bishkek');pg=await ctx.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    E=pg.evaluate
    async def boot(day):
      await pg.goto(URL);await E(SETUP,day);await pg.goto(URL);await pg.wait_for_timeout(300)
    # день 12 должен быть пятницей — подбираем «сегодня»
    await pg.goto(URL);wd=await E("new Date().getDay()")
    day=12 if wd==5 else None
    await boot(12)
    isfri=await E("DAYS[curDay()-1].fri?true:false")
    # ---------- анкета
    async def screen(risks,exp='0',pick=None):
      await E("document.querySelectorAll('#ov').forEach(o=>o.remove());delete S.fastScr;fastScreen(12,m=>{window.__m=m})")
      await E(f"document.querySelector('[data-e=\"{exp}\"]').click()")
      for r in risks: await E(f"document.querySelector('[data-r=\"{r}\"]').click()")
      await E("document.querySelector('#rn').click()")
      return await E("(()=>{const o=document.querySelector('#ov');return {t:o.textContent,doc:!!o.querySelector('[data-f=doctor]'),btns:[...o.querySelectorAll('[data-f]')].map(b=>b.dataset.f)}})()")
    for r in ['preg','ed','minor']:
      x=await screen([r])
      ok(f'№1 «{r}»: длительная пауза недоступна, «Врач разрешил» нет',not x['doc'] and x['btns']==['unload'],x['btns'])
    x=await screen(['heart'])
    ok('№1 болезнь сердца: «Врач разрешил» есть',x['doc'])
    await E("document.querySelector('[data-f=doctor]').click()")
    ok('  после «Врач разрешил» — ступень 24 ч',await E("S.fastScr.ok&&S.fastScr.level===24"))
    x=await screen([],'48')
    f0=await E("document.querySelector('#ov [data-f]').dataset.f")
    ok('№4 опыт 36–48 ч — всё равно первая ступень 24 ч',f0=='24' and 'Все начинают с 24 часов' in x['t'],f0)
    await E("document.querySelector('[data-f=\"24\"]').click()")
    ok('  анкета: level 24',await E("S.fastScr.level===24"))
    # ---------- №5 зачёт
    r=await E("[fastOkMs(24)/36e5,fastOkMs(36)/36e5,fastOkMs(48)/36e5]")
    ok('№5 зачёт ступени: 21,6 / 32,4 / 42 ч',[round(v,1) for v in r]==[21.6,32.4,42.0],r)
    # ---------- №3 старт только в свою пятницу
    r=await E("(()=>{S.fastScr={ok:true,level:36,risks:[]};S.days[19]={friMode:'fast'};const a=renderDay(19),b=renderDay(5);return [a.includes('fast-start'),a.includes('в четверг после 15:00'),fastCanStart(19),fastCanStart(curDay())]})()")
    ok('№3 будущая пятница (день 19): кнопки старта нет, есть пояснение',r[0] is False and r[1] and r[2] is False,r)
    if isfri: ok('№3 сегодняшняя пятница: старт можно',r[3])
    # подготовительные дни: старт программы в будущем
    r=await E("(()=>{const s0=S.profile.start;const d=new Date();d.setDate(d.getDate()+3);S.profile.start=d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');const c=[5,12,19,26].some(fastCanStart);S.profile.start=s0;return c})()")
    ok('№3 в подготовке ни одну пятницу начать нельзя',r is False)
    # №2 без анкеты — нет кнопки старта (раньше подставлялось 24 ч)
    r=await E("(()=>{delete S.fastScr;S.days[12]={friMode:'fast'};const h=renderDay(12);return [h.includes('fast-start'),h.includes('fast-screen')||!DAYS[11].fri]})()")
    ok('№2 анкета сброшена — старта нет, предлагается анкета',r==[False,True],r)
    r=await E("(()=>{S.days[12]={friMode:'fast'};S.mdays={};S.fastScr={ok:true,level:24};VIEW.tab='me';render();document.querySelector('#refast')&&document.querySelector('#refast').click();return [S.fastScr===undefined,S.days[12].friMode]})()")
    ok('№2 «Пройти анкету заново» сбрасывает выбор «пауза»',r==[True,None],r)
    # ---------- №6 баннер паузы на любом экране + «Завершить»
    r=await E("""(()=>{S.fastScr={ok:true,level:24,risks:[]};fastBegin(12,24);S.fast.start=Date.now()-5*36e5;save();VIEW={tab:'plan',day:null};render();
      const a=!!document.querySelector('#fb-end');VIEW={tab:'today',day:13};render();const b=!!document.querySelector('#fb-end');return [a,b]})()""")
    ok('№6 идущая пауза: баннер с «Завершить» на вкладке «План» и в другом дне',r==[True,True],r)
    await E("document.querySelector('#fb-bad').click()");await pg.wait_for_timeout(100)
    r=await E("document.querySelector('#ov').textContent")
    ok('№6 «Мне плохо» → когда звонить 103/112 и кнопка «Завершаю паузу и ем»','103' in r and 'Завершаю паузу' in r)
    await E("document.querySelector('#fb-stop').click()")
    r=await E("[!!S.fast.end,S.fast.felt,(S.fasts||[]).length,(S.fasts||[])[0].end>0]")
    ok('№6/№19 пауза завершена, отмечено «тяжело», записана в историю',r==[True,'hard',1,True],r)
    # ---------- №19 две паузы — обе в истории
    r=await E("(()=>{fastBegin(19,24);S.fast.start=Date.now()-25*36e5;fastEnd();return [S.fasts.length,S.fasts.map(f=>f.day)]})()")
    ok('№19 вторая пауза не затирает первую',r[0]==2,r)
    # ---------- №12 первая неделя
    r=await E("[DAYS[4].dish.includes('длительная'),renderPlan().includes('длительной паузы на 1-й неделе нет')]")
    ok('№12 1-я неделя: в карточке и плане нет длительной паузы',r==[False,True],r)
    # ---------- SOS
    r=await E("""(()=>{S.sos=[];sosOpen();SOS.trig='hunger';SOS.step='q';sosRender();const t=document.querySelector('#ov').textContent;document.querySelector('[data-res=eat]').click();
      const d=document.querySelector('#ov').textContent;sosClose();VIEW={tab:'progress'};render();return [t.includes('Поем по плану'),d.includes('Отлично'),document.querySelector('#app').textContent.includes('100%')]})()""")
    ok('SOS: голод → «Поем по плану»; осознанная еда — успех (100 %)',r==[True,True,True],r)
    r=await E("(()=>{sosOpen();SOS.trig='stress';SOS.step='q';sosRender();const t=document.querySelector('#ov').textContent;sosClose();return t})()")
    ok('SOS: без «отработки» упражнениями (приседания, планка)','приседан' not in r and 'планк' not in r)
    # ---------- добавки вне процента
    r=await E("(()=>{S.days[10]={};const a=score(10);S.days[10]={chk:{supp:true,mg:true}};const b=score(10);return [a,b,renderDay(10).includes('по согласованию с врачом')]})()")
    ok('добавки не влияют на процент дня, подписаны «по согласованию с врачом»',r[0]==r[1] and r[2],r)
    # ---------- нагрузка в день паузы
    r=await E("(()=>{S.days[26]={friMode:'fast'};const L=dayLoad(26),d=DAYS[25];return [d.stepsMin,L.stepsMin,d.plank,L.plank,d.ex.map(e=>e.s),L.ex.map(e=>e.s)]})()")
    ok('день длительной паузы (26): шаги, планка, подходы — вдвое меньше',r[1]*2==r[0] and abs(r[3]*2-r[2])<=10 and all(b_<=a_ for a_,b_ in zip(r[4],r[5])),r)
    # ---------- вода
    r=await E("(()=>{S.days={};const n=waterNorm(3);return [n.ml,n.parts[0][0]]})()")
    ok('вода: 95 кг / 180 см → скорректированный вес 86 кг × 35 = 3000 мл',r[0]==3000 and 'скорректированный' in r[1],r)
    # ---------- num / экранирование / слияние
    r=await E("[num('123abc'),num('-5'),num('72,5'),num('10 000'),glassMl()]")
    ok('№32 числа: «123abc» и «−5» не числа; «72,5» и «10 000» — да',r==[None,None,72.5,10000,250],r)
    r=await E("(()=>{S.profile.w0='<b>x';S.final=S.final||{};const h=renderFinal();S.profile.w0='95';return h.includes('&lt;b&gt;x')&&!h.includes('<b>x')})()")
    ok('№31 итоговый отчёт: введённый текст — как текст',r)
    r=await E("JSON.stringify(deepMerge({days:{3:{sets:{squat:[true,true,false]}}},sos:[{ts:1,res:'eat'}]},{days:{3:{sets:{squat:[true,false,true]}}},sos:[{ts:2,res:'passed'}]}))")
    d=json.loads(r)
    ok('№20 слияние: подходы по позициям (не «уникальные значения»), SOS объединены',d['days']['3']['sets']['squat']==[True,False,True] and len(d['sos'])==2,r)
    # ---------- сбой записи
    r=await E("""(()=>{const o=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){if(k==='gipno_v1')throw new Error('Quota');return o.call(this,k,v)};const a=save(true);Storage.prototype.setItem=o;return [a,document.querySelector('#toast').textContent]})()""")
    await pg.wait_for_timeout(50);t=await E("document.querySelector('#toast').textContent")
    ok('№22 запись не удалась — save() = false и сообщение',r[0] is False and 'память' in t,t)
    # ---------- другой аккаунт
    r=await E("""(async()=>{S._uid='A';save(true);CL.user={uid:'B',email:'b@x'};const DOC={get:async()=>({exists:false}),set:async()=>{window.__pushed=1}};CL.db={collection:()=>({doc:()=>({collection:()=>({doc:()=>DOC})})})};
      const pr=cloudPull(true);await new Promise(r=>setTimeout(r,100));const q=document.body.textContent.includes('дневник другого аккаунта');
      [...document.querySelectorAll('[data-a]')].find(b=>b.textContent.includes('Начать с нуля')).click();await pr;
      return [q,!S.profile,S._uid,!!localStorage.getItem('gipno_v1_acc_A'),!window.__pushed]})()""")
    ok('№18 вход другого аккаунта: спрашивает; «Начать с нуля» — чужой дневник не уходит в облако, сохранён отдельно',r==[True,True,'B',True,True],r)
    # ---------- сопровождение 90+
    await boot(30+95)
    r=await E("document.body.textContent")
    ok('после 90 дней поддержки: «Сопровождение • день 95»','Сопровождение • день 95' in r and 'день 90 из 90' not in r)
    # ---------- повреждённые данные
    await pg.goto(URL.replace('index.html','blank.html'));await E("localStorage.setItem('gipno_v1','{bad json')");await pg.goto(URL);await pg.wait_for_timeout(300)
    r=await E("Object.keys(localStorage).some(k=>k.startsWith('gipno_v1_broken_'))")
    ok('№22 повреждённые данные отложены, а не затёрты',r)
    ok('без ошибок JS',not errs,errs[:3])
    await b.close()
asyncio.run(m());print(f'{sum(R)}/{len(R)}'+(' PASS' if all(R) else ''))
