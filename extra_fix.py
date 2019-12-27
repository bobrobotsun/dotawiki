import json

with open('database/json_base.json',mode='r') as f:
    it=f.read()
    jt=json.loads(it)
for i in jt:
    for j in jt[i]:
        if '技能传递' in jt[i][j]:
            jt[i][j]['技能共享']=jt[i][j]['技能传递']
            jt[i][j].pop('技能传递')
            print(jt[i][j])

with open('database/json_base.json',mode='w') as f:
    f.write(json.dumps(jt))