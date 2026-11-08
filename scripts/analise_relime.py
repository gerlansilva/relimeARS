#!/usr/bin/env python3
"""Coautoria, palavras-chave e cocitação da RELIME (exportação CSV da Scopus).
Uso: python analise_relime.py arquivo.csv pasta_de_saida
Requer: pandas, numpy, networkx (>=3.0). Sementes fixas para reprodução."""
import sys, re, json, math, itertools, collections, unicodedata
import numpy as np, pandas as pd, networkx as nx
from networkx.algorithms.community import louvain_communities, modularity

CSV, OUT = sys.argv[1], sys.argv[2]
fold = lambda s: ''.join(c for c in unicodedata.normalize('NFKD', str(s)) if not unicodedata.combining(c)).lower()
d = pd.read_csv(CSV); d['year'] = d['Year'].astype(int)

# ---------- 1. Desambiguação: IDs diferentes com o mesmo nome completo normalizado ----------
nome_ids, nome_de = collections.defaultdict(set), {}
for v in d['Author full names'].astype(str):
    for n in v.split(';'):
        m = re.match(r'^(.*?)\s*\((\d+)\)\s*$', n.strip())
        if m: nome_ids[re.sub(r'[^a-z ,]', '', fold(m[1])).strip()].add(m[2]); nome_de.setdefault(m[2], m[1])
UNI = {}
for ids in nome_ids.values():
    if len(ids) > 1:
        for i in sorted(ids): UNI[i] = sorted(ids)[0]
grupos_id = collections.defaultdict(list)
for i, u in UNI.items(): grupos_id[u].append(i)
for u, ids in grupos_id.items():  # nome preferido: o variante com menos nomes após a vírgula
    nome_de[u] = sorted((nome_de[i] for i in ids), key=lambda v: (len(v.split(',')[1].split()) if ',' in v else 9, v))[0]
dup = sorted({nome_de[u] for u in grupos_id})
raw_ids = d['Author(s) ID'].fillna('').apply(lambda s: [x.strip() for x in s.split(';') if x.strip() and 'No author' not in x])
d['ids0'] = raw_ids
d['ids'] = raw_ids.apply(lambda l: list(dict.fromkeys(UNI.get(x, x) for x in l)))
sobrenome = lambda i: nome_de.get(i, i).split(',')[0].title()

# ---------- 2. Palavras-chave: normaliza acentos, caixa, plural, idiomas (ES/PT/FR/EN) ----------
STOP = set('de la el los las y e en of the and in a da do dos das du des et le les un una para por con no na em to for with on al del'.split())
CAN = {}
def grp(c, *ws):
    for w in ws: CAN[w] = c
grp('education', 'educacion', 'educacao', 'educational', 'educativa', 'educativo', 'educativos', 'educacionais')
grp('math', 'matematica', 'matematicas', 'mathematics', 'mathematical', 'mathematique', 'mathematiques', 'matematico', 'matematicos', 'maths')
grp('teaching', 'ensenanza', 'ensino', 'enseignement', 'ensenar')
grp('learning', 'aprendizaje', 'aprendizagem', 'apprentissage')
grp('teacher', 'profesor', 'profesores', 'professor', 'professores', 'teachers', 'docente', 'docentes', 'enseignant', 'enseignants')
grp('training', 'formacion', 'formacao', 'formation')
grp('problem', 'problema', 'problemas', 'problems', 'probleme', 'problemes')
grp('solving', 'resolucion', 'resolucao', 'resolution', 'resolver')
grp('model', 'modelo', 'modelos', 'modelacion', 'modelagem', 'modelizacion', 'modelisation', 'modeling', 'modelling', 'models')
grp('geometry', 'geometria', 'geometrie')
grp('calculus', 'calculo')
grp('statistics', 'estadistica', 'estatistica', 'statistique')
grp('probability', 'probabilidad', 'probabilidade', 'probabilite')
grp('function', 'funcion', 'funciones', 'funcao', 'funcoes', 'functions', 'fonction')
grp('algebra', 'algebraic', 'algebrico', 'algebraica')
grp('university', 'universitaria', 'universitario', 'universitaire', 'universidad', 'universidade', 'superior', 'higher')
grp('student', 'estudiante', 'estudiantes', 'estudante', 'estudantes', 'students', 'alumno', 'alumnos', 'aluno', 'alunos')
grp('knowledge', 'conocimiento', 'conhecimento', 'connaissance')
grp('space', 'espace', 'espacio', 'espaco')
grp('work', 'travail', 'trabajo', 'trabalho', 'working')
grp('resignification', 'resignificacion', 'resignificacao', 'resignify', 'resignificar')
grp('socioepistemology', 'socioepistemologia', 'socioepistemologie', 'socioepistemologica', 'socioepistemological')
grp('proportion', 'proporcion', 'proporcionalidad', 'proporcionalidade', 'proportionality')
grp('understanding', 'comprension', 'compreensao', 'comprehension')
grp('activity', 'actividad', 'atividade', 'activite')
grp('analysis', 'analisis', 'analise', 'analyse')
grp('data', 'datos', 'dados', 'donnees')
grp('theory', 'teoria', 'theorie')
grp('development', 'desarrollo', 'desenvolvimento', 'developpement')
grp('professional', 'profesional', 'profissional')
grp('practice', 'practica', 'pratica', 'pratique')
grp('number', 'numero', 'numeros', 'numbers')
grp('reasoning', 'razonamiento', 'raciocinio', 'raisonnement')
CANV = set(CAN.values())
def tok(t):
    t = CAN.get(t, t)
    return t[:-1] if t not in CANV and len(t) > 3 and t.endswith('s') and not t.endswith('ss') else t
def kkey(s): return ' '.join(sorted({tok(w) for w in re.findall(r'[a-z]+', re.sub(r'\be-(?=[a-z])', 'e', fold(s))) if w not in STOP}))  # e-learning != learning
orig = collections.defaultdict(collections.Counter)
def kws(s):
    if str(s) == 'nan': return []
    out = set()
    for k in str(s).split(';'):
        k = re.sub(r'^[\W_]+', '', re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', k.strip().lower())))
        if k: key = kkey(k); orig[key][k] += 1; out.add(key)
    return sorted(out)
d['kw'] = d['Author Keywords'].apply(kws)
rotulo = {k: sorted(c.items(), key=lambda x: (-x[1], x[0]))[0][0] for k, c in orig.items()}
n_orig = len({k for c in orig.values() for k in c}); n_chaves = len(orig)

# ---------- 3. Referências: texto normalizado (90 primeiros caracteres; fragmentos < 35 descartados) ----------
d['rf'] = d['References'].apply(lambda s: [] if str(s) == 'nan' else sorted({re.sub(r'\s+', ' ', fold(k).strip())[:90] for k in str(s).split(';') if len(k.strip()) >= 35}))

# ---------- 4. Redes de coautoria ----------
def build(df, col='ids'):
    G = nx.Graph()
    for l in df[col]:
        G.update(nodes=l); G.add_edges_from(itertools.combinations(l, 2))
    return G
def estrutura(df, col='ids'):
    G = build(df, col); cc = sorted(nx.connected_components(G), key=lambda c: (-len(c), sorted(c)[0]))
    comp = {a: i for i, c in enumerate(cc) for a in c}
    na = collections.Counter(comp[l[0]] for l in df[col] if l)
    multi = [i for i, v in sorted(na.items(), key=lambda x: (-x[1], -len(cc[x[0]]), x[0])) if v >= 2]
    cnt = collections.Counter(a for l in df[col] for a in l)
    return G, cc, comp, na, multi, cnt
G, cc, comp, na, multi, cnt = estrutura(d)
G0, cc0, _, na0, multi0, _ = estrutura(d, 'ids0')
H = G.subgraph([a for i in multi for a in cc[i]]).copy()
gig = G.subgraph(cc[0]); 
d['comp'] = d['ids'].apply(lambda l: comp[l[0]] if l else -1)
LET = 'ABCDEF'; letra = {c: LET[k] for k, c in enumerate(multi[:6])}
d['grp'] = d['comp'].map(lambda c: letra.get(c, '-'))
grp_tot = {letra[c]: na[c] for c in multi[:6]}
R = {}
res = dict(dup=dup, n_dup=len(dup))
res['orig'] = dict(autores=G0.number_of_nodes(), comps=len(cc0), multi=len(multi0), maior=len(cc0[0]))
res['uni'] = dict(autores=G.number_of_nodes(), comps=len(cc), multi=len(multi), art_multi=sum(na[i] for i in multi),
                  aut_multi=H.number_of_nodes(), lacos=H.number_of_edges(), dens=round(nx.density(H), 4),
                  maior=len(cc[0]), maior_lacos=gig.number_of_edges(), diam=nx.diameter(gig), art=len(d),
                  recorr=sum(v >= 2 for v in cnt.values()), tres=sum(v >= 3 for v in cnt.values()), um=sum(v == 1 for v in cnt.values()),
                  dens_g=round(nx.density(build(d)), 4), media_aut=round(d['ids'].apply(len).mean(), 2), sozinho=int((d['ids'].apply(len) == 1).sum()),
                  art_pontos=len(list(nx.articulation_points(H))), mult6=int((d['ids'].apply(len) >= 6).sum()))
G2, cc2, _, _, multi2, _ = estrutura(d[d['ids'].apply(len) < 6]); res['sem6'] = dict(comps=len(cc2), maior=len(cc2[0]), autores=G2.number_of_nodes())
res['grupos'] = []
for c in multi[:6]:
    S = G.subgraph(cc[c]); sub = d[d.comp == c]; cn = collections.Counter(a for l in sub['ids'] for a in l)
    kc = collections.Counter(k for l in sub['kw'] for k in l)
    res['grupos'].append(dict(l=letra[c], art=na[c], aut=len(S), lacos=S.number_of_edges(), dens=round(nx.density(S), 2),
        anos=f"{sub.year.min()}–{sub.year.max()}" if sub.year.min() != sub.year.max() else str(sub.year.min()),
        top=[sobrenome(a) for a, _ in cn.most_common(2)], kw=[rotulo[k] for k, _ in kc.most_common(3)], pontos=len(list(nx.articulation_points(S)))))

# períodos
res['per'] = {}
for nm, mask in (('p1', d.year <= 2016), ('p2', d.year > 2016)):
    df = d[mask]; g, c, cm, n_, mu, ct, = estrutura(df)[0:3] + (estrutura(df)[3], estrutura(df)[4], estrutura(df)[5])
    h = g.subgraph([a for i in mu for a in c[i]])
    res['per'][nm] = dict(art=len(df), aut=g.number_of_nodes(), comps=len(c), multi=len(mu), aut_multi=h.number_of_nodes(), lacos=h.number_of_edges(),
        rec=sum(1 for a in h if ct[a] >= 2), grupos=dict(collections.Counter(letra.get(comp[a], '-') for a in h)))
A1 = {a for l in d[d.year <= 2016]['ids'] for a in l}; A2 = {a for l in d[d.year > 2016]['ids'] for a in l}; res['ambos'] = len(A1 & A2)

# ---------- 5. Teste de vocabulário (Jaccard, permutação dos rótulos de componente) ----------
def perm(sets, labels, n=2000, seed=1):
    k = len(sets); J = np.zeros((k, k))
    for i in range(k):
        for j in range(i + 1, k):
            u = len(sets[i] | sets[j]); J[i, j] = J[j, i] = len(sets[i] & sets[j]) / u if u else 0
    iu = np.triu_indices(k, 1); Jv = J[iu]; lab = np.array(labels); same = lab[iu[0]] == lab[iu[1]]
    obs, btw = Jv[same].mean(), Jv[~same].mean(); rng = np.random.default_rng(seed); ge = 0
    for _ in range(n):
        l2 = rng.permutation(lab); ge += Jv[l2[iu[0]] == l2[iu[1]]].mean() >= obs
    return dict(dentro=round(obs, 4), entre=round(btw, 4), p=round((ge + 1) / (n + 1), 4), n=k)
m_ = d[d.comp.isin(multi)]
for nome, col in (('kw', 'kw'), ('rf', 'rf')):
    s_ = m_[m_[col].apply(len) > 0]; res['teste_' + nome] = perm([set(x) for x in s_[col]], list(s_.comp))

# ---------- 6. Referências compartilhadas entre componentes ----------
Rc = {i: set().union(*[set(x) for x in d[d.comp == i].rf]) for i in multi}
rc = collections.defaultdict(set)
for _, r in d.iterrows():
    for x in r.rf: rc[x].add(r.comp)
res['refs'] = dict(unicas=len(rc), em2=sum(len(s) >= 2 for s in rc.values()))
shared = {(i, j): len(Rc[i] & Rc[j]) for i, j in itertools.combinations(multi, 2)}
res['refs']['pares3'] = sum(v >= 3 for v in shared.values()); par = max(shared, key=shared.get)
res['refs']['top'] = [multi.index(par[0]), multi.index(par[1]), shared[par]]
res['refs']['pares'] = [[multi.index(a), multi.index(b), w] for (a, b), w in sorted(shared.items(), key=lambda x: -x[1])[:5]]

# ---------- 7. Redes de coocorrência (palavras-chave) e cocitação (referências) ----------
def cooc(lists, keep):
    g = nx.Graph()
    for l in lists:
        l = [x for x in l if x in keep]; g.add_nodes_from(l)
        for a, b in itertools.combinations(l, 2): g.add_edge(a, b, weight=g[a][b]['weight'] + 1 if g.has_edge(a, b) else 1)
    g.remove_nodes_from(list(nx.isolates(g))); return g
fk = collections.Counter(k for l in d.kw for k in l); fr = collections.Counter(x for l in d.rf for x in l)
K = cooc(d.kw, {k for k, v in fk.items() if v >= 2}); C = cooc(d.rf, {k for k, v in fr.items() if v >= 3})
res['K'] = dict(brutas=n_orig, harmon=n_chaves, nos=K.number_of_nodes(), arestas=K.number_of_edges(), com2=sum(v >= 2 for v in fk.values()), com_kw=int((d.kw.apply(len) > 0).sum()))
res['C'] = dict(nos=C.number_of_nodes(), arestas=C.number_of_edges())

# ---------- 8. Figuras em SVG (halos = comunidades; linhas cinzas = ligações entre elas) ----------
PAL = ['#534AB7', '#0F6E56', '#C4501F', '#185FA5', '#993556', '#5B7F1A', '#8A6A00']; GRAY = '#8f8d85'
def halo_svg(Gr, groups, colors, badges, meta, cls, W, Hh, label, unit=34, thr=3, nw=(7, 11, 15)):
    ids = list(range(len(groups))); M = nx.Graph(); M.add_nodes_from(ids)
    for (i, j), w in meta.items():
        if w >= 2: M.add_edge(i, j, weight=w)
    p0 = nx.spring_layout(M, seed=4, weight='weight', k=1.2, iterations=300); P0 = np.array([p0[i] for i in ids]); P0 = (P0 - P0.min(0)) / (np.ptp(P0, 0) + 1e-9)
    for _ in range(8):
        info = {}
        for i, g in enumerate(groups):
            S = Gr.subgraph(g); n = len(S)
            if n == 1: q = {next(iter(S)): np.zeros(2)}
            elif n == 2: a, b = list(S); q = {a: np.array([-1., 0]), b: np.array([1., 0])}
            else: q = {a: np.array(v) for a, v in nx.spring_layout(S, seed=5, iterations=300, k=1.3 / math.sqrt(n), weight='weight').items()}
            Q = np.array(list(q.values())); c0 = Q.mean(0); m = max(1e-6, np.abs(Q - c0).max()); D = unit * math.sqrt(n) + unit * 0.7
            info[i] = (S, {a: (q[a] - c0) / m * D / 2 for a in q}, D / 2 + 10)
        pos = {i: np.array([60 + P0[k, 0] * (W - 120), 60 + P0[k, 1] * (Hh - 120)]) for k, i in enumerate(ids)}
        for _ in range(600):
            for a, b in itertools.combinations(ids, 2):
                dv = pos[a] - pos[b]; dist = np.linalg.norm(dv) + 1e-6; need = info[a][2] + info[b][2] + 8
                if dist < need: s = (need - dist) / 2 * dv / dist; pos[a] += s; pos[b] -= s
            for i in ids: r = info[i][2]; pos[i] = np.clip(pos[i], [r + 6, r + 6], [W - r - 6, Hh - r - 6])
        if all(np.linalg.norm(pos[a] - pos[b]) >= info[a][2] + info[b][2] + 2 for a, b in itertools.combinations(ids, 2)): break
        unit *= 0.85
    h = ln = gr = bd = ''
    for i in ids: h += f'<circle cx="{round(pos[i][0])}" cy="{round(pos[i][1])}" r="{round(info[i][2])}" fill="{colors[i]}" fill-opacity="0.09"/>'
    for (i, j), w in sorted(meta.items(), key=lambda x: x[1]):
        if w >= thr: ln += f'<path d="M{round(pos[i][0])} {round(pos[i][1])}L{round(pos[j][0])} {round(pos[j][1])}" stroke-width="{round(2 + 1.2 * min(w, 12), 1)}"/>'
    for i in ids:
        S, q, r = info[i]; pp = {a: (round(pos[i][0] + q[a][0]), round(pos[i][1] + q[a][1])) for a in S}
        e = ''.join(f'M{pp[a][0]} {pp[a][1]}L{pp[b][0]} {pp[b][1]}' for a, b in S.edges()); nd = collections.defaultdict(str)
        for a in S: nd[cls(a)] += f'M{pp[a][0]} {pp[a][1]}h0'
        g = f'<g stroke="{colors[i]}" fill="none" stroke-linecap="round"><path d="{e}" stroke-width="1.4" opacity="0.55"/>'
        for k in (0, 1, 2):
            if nd[k]: g += f'<path d="{nd[k]}" stroke-width="{nw[k]}"/>'
        gr += g + '</g>'
        if badges[i]:
            v = pos[i] - np.array([W / 2, Hh / 2]); n = np.linalg.norm(v); v = v / n if n > 1e-6 else np.array([0, -1.]); b = pos[i] + v * r
            bx, by = min(max(b[0], 30), W - 30), min(max(b[1], 30), Hh - 30)
            bd += f'<circle cx="{round(bx)}" cy="{round(by)}" r="20" fill="#ffffff" stroke="{colors[i]}" stroke-width="3.5"/><text x="{round(bx)}" y="{round(by) + 9}" text-anchor="middle" font-size="26" font-weight="700" fill="{colors[i]}" font-family="Inter, Arial, sans-serif">{badges[i]}</text>'
    return f'<svg aria-label="{label}" style="width:{W}px;height:{Hh}px" viewBox="0 0 {W} {Hh}" width="{W}" height="{Hh}">{h}<g stroke="#d3d1c7" stroke-linecap="round" fill="none" opacity="0.95">{ln}</g>{gr}{bd}</svg>'
cls2 = lambda f, lo, hi: 0 if f <= lo else (1 if f <= hi else 2)
svgs = {}
# rede de coautoria: um círculo por componente com 2+ artigos, ligações = referências em comum
grp_nodes = [cc[i] for i in multi]
svgs['rede'] = halo_svg(G, grp_nodes, [PAL[k] if k < 6 else GRAY for k in range(len(multi))], [LET[k] if k < 6 else None for k in range(len(multi))],
    {(i, j): shared[(multi[i], multi[j])] for i, j in itertools.combinations(range(len(multi)), 2)}, lambda a: min(2, cnt[a] - 1), 1040, 700,
    'Rede de coautoria da RELIME: componentes com 2 ou mais artigos, ligados por referências em comum', unit=30, nw=(7, 11, 15))
for nm, mask in (('p1', d.year <= 2016), ('p2', d.year > 2016)):
    g_, c_, cm_, na_, mu_, ct_ = estrutura(d[mask])
    svgs[nm] = halo_svg(g_, [c_[i] for i in mu_], [PAL[LET.index(letra[comp[next(iter(c_[i]))]])] if comp[next(iter(c_[i]))] in letra else GRAY for i in mu_],
        [None] * len(mu_), {}, lambda a: min(2, ct_[a] - 1), 764, 400, 'Rede de coautoria no período', unit=20, nw=(6, 9, 12))
def comunidades(Gr, freq, minimo, nome, ord_):
    cm = sorted(louvain_communities(Gr, weight='weight', seed=3), key=lambda c: -sum(freq[x] for x in c)); rk = {x: k for k, c in enumerate(cm) for x in c}
    meta = collections.Counter()
    for a, b, w in Gr.edges(data='weight'):
        if rk[a] != rk[b]: meta[tuple(sorted((rk[a], rk[b])))] += w
    cor = [PAL[k] if len(c) >= minimo and k < 7 else GRAY for k, c in enumerate(cm)]
    svg = halo_svg(Gr, cm, cor, [str(k + 1) if cor[k] != GRAY else None for k in range(len(cm))], meta, lambda a: cls2(freq[a], ord_[0], ord_[1]), 1040, 700, nome, unit=34)
    return cm, modularity(Gr, cm, weight='weight'), svg
def afinidade(cm, col):
    out = []
    for c in cm:
        s = set(c); sub = d[d[col].apply(lambda l: any(x in s for x in l))]; gc = collections.Counter(sub.grp); gc.pop('-', None)
        best = max(((n / grp_tot[g], n, g) for g, n in gc.items()), default=None)
        out.append(dict(grupo=best[2] if best and best[0] >= .5 else None, na=best[1] if best else 0, tot=grp_tot.get(best[2], 0) if best else 0))
    return out
cmK, modK, svgs['kw'] = comunidades(K, fk, 7, 'Rede de coocorrência de palavras-chave em comunidades temáticas', (2, 4))
cmC, modC, svgs['cocit'] = comunidades(C, fr, 5, 'Rede de cocitação de referências em comunidades', (4, 6))
afK, afC = afinidade(cmK, 'kw'), afinidade(cmC, 'rf')
res['K'].update(mod=round(modK, 3), com=[dict(n=len(c), top=[rotulo[x] for x in sorted(c, key=lambda x: -fk[x])[:3]], **a) for c, a in zip(cmK, afK)])
def autor_ref(s):
    m = re.match(r"^([^,]{2,40}?) ((?:[a-z]\.-?)+),\s*(.*)$", s); return (m[1].title() if m else re.sub(r',?\s*\(\d{4}\).*$', '', s)[:45].capitalize())
res['C'].update(mod=round(modC, 3), com=[dict(n=len(c), top=[], **a) for c, a in zip(cmC, afC)])
for k, c in enumerate(cmC):
    ac = collections.Counter()
    for x in c: ac[autor_ref(x)] += fr[x]
    res['C']['com'][k]['top'] = [a for a, _ in ac.most_common(3)]
import os; os.makedirs(OUT, exist_ok=True)
for k, v in svgs.items(): open(f'{OUT}/{k}.svg', 'w').write(v)
json.dump(res, open(f'{OUT}/resultados.json', 'w'), ensure_ascii=False, indent=1)
print(json.dumps({k: res[k] for k in ('dup', 'orig', 'uni', 'sem6', 'ambos', 'teste_kw', 'teste_rf', 'refs')}, ensure_ascii=False))
print('K', {k: res['K'][k] for k in ('brutas', 'harmon', 'nos', 'arestas', 'com2', 'mod')}, [c['n'] for c in res['K']['com']])
print('C', {k: res['C'][k] for k in ('nos', 'arestas', 'mod')}, [c['n'] for c in res['C']['com']])
print('periodos', res['per'])
for g in res['grupos']: print(g)
