# Сборка index.html: python3 src/build.py
import os
d=os.path.dirname(os.path.abspath(__file__))
t=open(os.path.join(d,'template.html'),encoding='utf-8').read()
t=t.replace('/*DAYS*/',open(os.path.join(d,'days.json'),encoding='utf-8').read()).replace('/*SECS*/',open(os.path.join(d,'secs.json'),encoding='utf-8').read())
open(os.path.join(d,'..','index.html'),'w',encoding='utf-8').write(t)
print('index.html собран')
