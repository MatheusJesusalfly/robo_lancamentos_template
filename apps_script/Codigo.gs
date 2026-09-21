/**
 * Recebe a venda do robo e acrescenta uma linha na planilha.
 *
 * COMO INSTALAR
 *   1. Abra a sua planilha no Google Sheets.
 *   2. Extensoes -> Apps Script. Apague o que estiver la e cole isto.
 *   3. Troque o SEGREDO abaixo por uma palavra sua.
 *   4. Implantar -> Nova implantacao -> Tipo: app da Web.
 *      Executar como: eu.  Quem tem acesso: qualquer pessoa.
 *   5. Copie a URL para PLANILHA_URL no .env, e o segredo para PLANILHA_SEGREDO.
 *
 * POR QUE O SEGREDO
 *   "Qualquer pessoa" significa qualquer pessoa mesmo: a URL e publica. Sem
 *   este segredo, quem descobrir o endereco escreve linhas na sua planilha.
 */

const SEGREDO = 'troque-isto';

function doPost(e) {
  try {
    const dados = JSON.parse(e.postData.contents);
    if (dados.segredo !== SEGREDO) {
      return _json({ ok: false, erro: 'segredo errado' });
    }
    const aba = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
    aba.appendRow([
      new Date(),
      dados.cliente,
      dados.descricao,
      Number(dados.faturamento),
      Number(dados.custo),
      Number(dados.lucro),
      dados.observacao || '',
    ]);
    return _json({ ok: true, linha: aba.getLastRow() });
  } catch (erro) {
    // Devolve o erro no corpo com status 200 porque o Apps Script nao deixa
    // escolher o status. E exatamente por isso que o robo le o corpo.
    return _json({ ok: false, erro: String(erro) });
  }
}

function _json(objeto) {
  return ContentService
    .createTextOutput(JSON.stringify(objeto))
    .setMimeType(ContentService.MimeType.JSON);
}
