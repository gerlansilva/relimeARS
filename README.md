# RELIME — Atlas de redes

Site estático de exploração de redes da produção científica da *Revista Latinoamericana de Investigación en Matemática Educativa* (RELIME).

## Conteúdo

A página contém cinco redes interativas: coautoria, instituições, países, palavras-chave e referências cocitadas, com filtros de período, busca, zoom, detalhes e exportação de dados. O conjunto de dados está incorporado em `index.html`.

**Corpus informado na página:** 221 artigos, 2009–2024. **Fonte declarada na página:** exportação Scopus fornecida pelo pesquisador; processamento de 7 de novembro de 2026. Consulte as notas metodológicas e de qualidade na própria interface antes de interpretar as relações.

## Uso local

Abra `index.html` em um navegador moderno. Não há necessidade de instalar pacotes ou executar build.

## Publicação no Cloudflare Pages

1. Crie um repositório público no GitHub, por exemplo `gerlansilva/relime-redes`.
2. Envie todos os arquivos desta pasta à raiz do repositório (principalmente `index.html`).
3. No Cloudflare, vá a **Workers & Pages → Create → Pages → Connect to Git** e conecte o repositório.
4. Configure **Framework preset** = `None`, **Build command** = vazio e **Build output directory** = `/` (diretório raiz).
5. Publique. Commits posteriores no ramo de produção acionam novas publicações.

Alternativa: em **Workers & Pages**, use a opção de upload direto para publicar a pasta ou o ZIP, mas isso não configura atualização automática a partir do GitHub.

## Organização

- `index.html`: interface, estilos, scripts e dados completos.
- `README.md`: documentação de publicação e uso.
- `.gitignore`: arquivos locais que não precisam entrar no repositório.

Este projeto é independente dos repositórios de memória científica já existentes.
