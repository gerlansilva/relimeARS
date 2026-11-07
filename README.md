# RELIME — Atlas de redes (v1.1)

Site estático para explorar as redes da produção científica da *Revista Latinoamericana de Investigación en Matemática Educativa* (RELIME): coautoria, instituições, países, palavras-chave e referências cocitadas. Corpus: 221 artigos, 2009–2024, exportação da Scopus.

## O que há de novo na v1.1

- **Autores desambiguados.** Quatro autores com dois IDs da Scopus cada (Cordero Osorio, Farfán, Oktaç e Parraguez), confirmados pelo nome completo normalizado, foram unificados. A rede passa de 483 para 479 autores e de 152 para 150 componentes. A lista está em `idMerges` no JSON de dados.
- **Resultados reproduzíveis.** Nova seção na página, com figuras (SVG), tabelas (CSV), teste de vocabulário, redes por período e sensibilidade à desambiguação. Tudo é gerado por `scripts/analise_relime.py`.
- **Links da vista.** O endereço (`#k=...&f=...`) guarda rede, período, filtros e nó selecionado; o botão “Copiar link da vista” facilita citar uma figura do atlas no texto.
- **Exportação com legenda.** O SVG exportado traz fonte, regras de cor e versão.
- **Impressão.** A página oculta controles ao imprimir.

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
- A harmonização de palavras-chave (acentos, plurais, equivalentes em espanhol, português, francês e inglês) vale para a seção de resultados; as abas do atlas mantêm sinônimos e traduções separados.
- Coautoria é um indício de interação, não de pertencimento a um coletivo de pensamento. A semelhança de vocabulário dentro dos grupos pode vir de autocitação.
- Os grupos D, E e F têm 4 artigos cada.

## Estrutura

- `index.html`: interface, estilos, scripts e dados.
- `scripts/analise_relime.py`: análise e figuras.
- `CITATION.cff`: metadados para citação.

## Como citar

Veja `CITATION.cff`. Antes de submeter o artigo, publique uma versão no Zenodo (Releases do GitHub) para obter um DOI e atualize o arquivo.
