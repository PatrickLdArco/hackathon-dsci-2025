# Sistema de Atualização de Conteúdos Educacionais

Este projeto foi desenvolvido durante um hackathon e tem como objetivo auxiliar editores educacionais na atualização de apostilas e outros conteúdos educacionais. O sistema identifica pontos que podem ser ajustados com base em feedbacks recebidos e destaca informações mutáveis, como datas, nomes de presidentes, representantes, entre outros.

## Funcionalidades

- **Análise de Feedbacks**: Processa feedbacks recebidos para identificar áreas de melhoria nos conteúdos educacionais.
- **Identificação de Informações Mutáveis**: Detecta informações sensíveis a mudanças, como datas e nomes, para facilitar atualizações futuras.
- **Automatização de Ajustes**: Sugere alterações com base nos feedbacks e nas informações mutáveis identificadas.

## Como Testar

1. Preencha os arquivos CSV localizados em `data/feedbacks/`:
   - `ajustes.csv`: Contém as informações que precisam ser ajustadas.
   - `feedbacks.csv`: Contém os feedbacks recebidos.

2. Certifique-se de que o `python-tk` está instalado no seu sistema. Siga as instruções abaixo para o seu sistema operacional:

   - **Ubuntu**:
     ```bash
     sudo apt-get install python3-tk
     ```

   - **Fedora**:
     ```bash
     sudo dnf install python3-tkinter
     ```

   - **macOS**:
     ```bash
     brew install python-tk
     ```

3. Após preencher os arquivos, execute o seguinte comando no terminal (comando será adicionado posteriormente).



## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

---

Este projeto foi desenvolvido com o objetivo de facilitar o trabalho de editores educacionais e promover a melhoria contínua dos materiais educacionais.