#!/usr/bin/env python3
"""권 개관의 '다른 권과의 연결' 수치를 만든다 (66권 모두 같은 방법).

사용법:  python crossref_links.py <권 번호 1~66> <cross_references.txt 경로>
자료:    OpenBible.info Cross-references (CC BY) https://www.openbible.info/labs/cross-references/
출력:    권 개관 JSON에 넣을 `links` 블록과 `sections`용 문장(JSON)을 표준 출력으로 낸다.
주의:    득표는 '함께 읽을 연결'을 지지한 정도이며 인용·영향을 판정한 값이 아니다.
"""
import sys,json
PATH=sys.argv[2] if len(sys.argv)>2 else 'cross_references.txt'
import re,json,collections
BOOKS="창세기 출애굽기 레위기 민수기 신명기 여호수아 사사기 룻기 사무엘상 사무엘하 열왕기상 열왕기하 역대상 역대하 에스라 느헤미야 에스더 욥기 시편 잠언 전도서 아가 이사야 예레미야 예레미야애가 에스겔 다니엘 호세아 요엘 아모스 오바댜 요나 미가 나훔 하박국 스바냐 학개 스가랴 말라기 마태복음 마가복음 누가복음 요한복음 사도행전 로마서 고린도전서 고린도후서 갈라디아서 에베소서 빌립보서 골로새서 데살로니가전서 데살로니가후서 디모데전서 디모데후서 디도서 빌레몬서 히브리서 야고보서 베드로전서 베드로후서 요한일서 요한이서 요한삼서 유다서 요한계시록".split()
OSIS="Gen Exod Lev Num Deut Josh Judg Ruth 1Sam 2Sam 1Kgs 2Kgs 1Chr 2Chr Ezra Neh Esth Job Ps Prov Eccl Song Isa Jer Lam Ezek Dan Hos Joel Amos Obad Jonah Mic Nah Hab Zeph Hag Zech Mal Matt Mark Luke John Acts Rom 1Cor 2Cor Gal Eph Phil Col 1Thess 2Thess 1Tim 2Tim Titus Phlm Heb Jas 1Pet 2Pet 1John 2John 3John Jude Rev".split()
IDX={o:i+1 for i,o in enumerate(OSIS)}
SHORT="창 출 레 민 신 수 삿 룻 삼상 삼하 왕상 왕하 대상 대하 스 느 에 욥 시 잠 전 아 사 렘 애 겔 단 호 욜 암 옵 욘 미 나 합 습 학 슥 말 마 막 눅 요 행 롬 고전 고후 갈 엡 빌 골 살전 살후 딤전 딤후 딛 몬 히 약 벧전 벧후 요일 요이 요삼 유 계".split()
def parse(v):
    m=re.match(r'(\w+)\.(\d+)\.(\d+)$',v); 
    return (IDX[m.group(1)],int(m.group(2)),int(m.group(3))) if m else None
def fmt(t,full=False):
    b,c,v=t; return f"{SHORT[b-1]} {c}:{v}"
def fmt_range(a,b):
    ta,tb=parse(a),parse(b) if b else None
    if not tb or tb==ta: return fmt(ta)
    if ta[0]==tb[0] and ta[1]==tb[1]: return f"{fmt(ta)}–{tb[2]}"
    if ta[0]==tb[0]: return f"{fmt(ta)}–{tb[1]}:{tb[2]}"
    return f"{fmt(ta)}–{fmt(tb)}"
def load():
    rows=[]
    for l in open(PATH,encoding='utf8').read().split('\n')[1:]:
        p=l.split('\t')
        if len(p)<3: continue
        a=p[0]; bb=p[1]; 
        b1,_,b2=bb.partition('-')
        ta=parse(a); tb=parse(b1)
        if not ta or not tb: continue
        try: votes=int(p[2])
        except: continue
        rows.append((a,b1,b2 or None,ta,tb,votes))
    return rows
def book_links(bn,top=8):
    rows=load()
    other=collections.Counter();votes=collections.Counter();chap=collections.Counter();pairs=[]
    n=0
    for a,b1,b2,ta,tb,v in rows:
        if v<=0: continue
        if ta[0]==bn and tb[0]!=bn: here,there,rr=ta,tb,(a,b1,b2); outdir=True
        elif tb[0]==bn and ta[0]!=bn: here,there,rr=tb,ta,(a,b1,b2); outdir=False
        else: continue
        n+=1; other[there[0]]+=1; votes[there[0]]+=v; chap[here[1]]+=1
        pairs.append((v,here,there,outdir,rr))
    return n,other,votes,chap,sorted(pairs,key=lambda x:-x[0])

def make(bn):
    n,other,votes,chap,pairs=book_links(bn)
    nt=sum(c for bk,c in other.items() if bk>=40); ot=n-nt
    name=BOOKS[bn-1]
    S=[f"OpenBible.info 상호참조 자료(득표가 0보다 큰 항목)에서 {name} 구절을 다른 권의 구절과 잇는 연결은 모두 {n:,}건이다.",
       f"이 가운데 구약의 다른 권과의 연결은 {ot:,}건, 신약과의 연결은 {nt:,}건이다.",
       "연결이 가장 많은 책은 "+", ".join(f"{BOOKS[k-1]}({c:,}건)" for k,c in other.most_common(8))+" 순이다.",
       f"{name} 안에서 다른 권과의 연결이 가장 많이 몰린 장은 "+", ".join(f"{c}장({k:,}건)" for c,k in chap.most_common(6))+" 순이다."]
    seen=set();out=[]
    for v,h,t,o,rr in pairs:
        if (h,t) in seen: continue
        seen.add((h,t)); out.append(f"{fmt(h)} ↔ {fmt(t)}({v}표)")
        if len(out)==6: break
    S.append("득표가 가장 많은 연결은 "+", ".join(out)+" 등이다.")
    return dict(sentences=S,links=dict(total=n,ot=ot,nt=nt,
        byBook=[dict(book=k,name=BOOKS[k-1],count=c,votes=votes[k]) for k,c in other.most_common(12)],
        topChapters=[dict(chapter=c,count=k) for c,k in chap.most_common(10)],
        topPairs=[dict(here=fmt(h),there=fmt(t),votes=v) for v,h,t,o,rr in pairs[:20]]))
if __name__=='__main__':
    print(json.dumps(make(int(sys.argv[1])),ensure_ascii=False,indent=1))
