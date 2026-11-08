# RELIME — Atlas de redes (v1.1)

Site estático para explorar as redes da produção científica da *Revista Latinoamericana de Investigación en Matemática Educativa* (RELIME): coautoria, instituições, países, palavras-chave e referências cocitadas. Corpus: 221 artigos, 2009–2024, exportação da Scopus.

## O que há de novo na v1.1

**Interface**
- Mapa em tela cheia: a área de visualização ocupa a janela inteira abaixo de uma barra compacta.
- Filtros e Detalhes são painéis flutuantes que se abrem e fecham (botões na barra); o painel de Detalhes abre sozinho ao selecionar um nó.
- Modo foco (tecla F; Esc para sair) esconde toda a interface. Há também tela cheia.
- Legenda recolhível sob o mapa; seções de resultados, referencial e método em cartões recolhíveis.
- Botão “Copiar link da vista”: o endereço (`#k=...`) guarda rede, período, filtros e nó selecionado.
- Exportação em SVG com legenda, fonte e versão. Impressão sem controles.

**Dados**
- Autores desambiguados: quatro autores com dois IDs da Scopus cada (Cordero Osorio, Farfán, Oktaç e Parraguez), confirmados pelo nome completo normalizado, foram unificados (483 para 479 autores; 152 para 150 componentes). Lista em `idMerges` no JSON.
- Palavras-chave harmonizadas (759 para 704 termos): sem acento, caixa nem plural, e com equivalentes em espanhol, português, francês e inglês. O rótulo é a forma mais frequente; as formas originais aparecem em “Variantes unificadas”. Regra automática, não revisada à mão (revise em `keywordHarmonization.exemplos`). Comunidades e layouts da rede foram recalculados.

**Texto científico**
- Seção “Resultados reproduzíveis”: figuras (SVG), tabelas (CSV), teste de vocabulário, redes por período e sensibilidade à desambiguação, gerados por `scripts/analise_relime.py`.
- Cartão “Referencial: Fleck e análise de redes”: o coletivo de pensamento é a categoria analítica central; o estilo de pensamento é hipótese a verificar na leitura dos textos, não variável medida. Inclui o quadro de correspondências e limites.

## Uso local

Abra `index.html` em um navegador moderno. Não há build nem dependências.

## Publicação

**GitHub Pages:** *Settings → Pages → Build and deployment → Deploy from a branch → `main` / `(root)`*.
**Cloudflare Pages:** *Workers & Pages → Create → Pages → Connect to Git*; *Framework preset* = `None`, *Build command* vazio, *Build output directory* = `/`.

## Reprodução da análise

```bash
pip install pandas numpy networkx
python scripts/analise_relime.py exportacao_scopus.csv saida/
```

Gera `saida/resultados.json` e as figuras SVG usadas na seção de resultados. Sementes fixas (Louvain: 3; permutações: 1; layouts: 4 e 5). Versões usadas: Python 3.12.3, networkx 3.7, NumPy 2.5.4, pandas 3.0.6.

## Dados e cuidados

- O arquivo `index.html` contém o conjunto de dados derivado da exportação da Scopus (títulos, DOIs, autores, afiliações, palavras-chave e referências). **O CSV original não está no repositório.** Verifique os termos de uso da Scopus/Elsevier antes de redistribuí-lo.
- A harmonização de palavras-chave é automática e pode juntar o que não deveria (por exemplo, “Content knowledge” e “Pedagogical content knowledge”) ou deixar de juntar; revise antes de publicar.
- Coautoria é um indício de interação, não de pertencimento a um coletivo de pensamento. A semelhança de vocabulário dentro dos grupos pode vir de autocitação.
- Os grupos D, E e F têm 4 artigos cada.

## Estrutura

- `index.html`: interface, estilos, scripts e dados.
- `scripts/analise_relime.py`: análise e figuras.
- `CITATION.cff`: metadados para citação.

## Como citar

Veja `CITATION.cff`. Antes de submeter o artigo, publique uma versão no Zenodo (Releases do GitHub) para obter um DOI e atualize o arquivo.
