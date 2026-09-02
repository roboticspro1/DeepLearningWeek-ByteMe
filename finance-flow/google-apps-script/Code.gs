const EXPENSE_HEADERS = ['ID','Date','Description','Category','Funding Source','Quantity','Unit Price (SGD)','Total (SGD)','Paid By','Payment Source','Reimbursement Status','Reimbursement Due','Approval Status','Notes','Invoice / Receipt','Created At'];
const GRANT_HEADERS = ['Grant Name','Award Amount (SGD)','Status','Notes','Created At'];
const EARNING_HEADERS = ['ID','Date','Description','Quantity','Unit Price (SGD)','Revenue Type','Customer / Payer','Total (SGD)','Reference','Invoice / Receipt','Created At'];

function doGet() {
  const resources = getResources_();
  return json_({ok:true, message:'PhysiCode Finance connector is running', spreadsheetUrl:resources.spreadsheet.getUrl(), folderUrl:resources.folder.getUrl()});
}
function doPost(event) {
  try {
    const payload = JSON.parse(event.postData.contents), resources = getResources_();
    if (payload.action === 'addGrant') return addGrant_(resources, payload.grant);
    if (payload.action === 'updateGrant') return updateGrant_(resources, payload.grant, payload.oldName);
    if (payload.action === 'deleteGrant') return deleteGrant_(resources, payload.name, payload.reassign);
    if (payload.action === 'addExpense') return addExpense_(resources, payload.expense, payload.file);
    if (payload.action === 'addEarning') return addEarning_(resources, payload.earning, payload.file);
    if (payload.action === 'updateExpense') return updateExpense_(resources, payload.expense, payload.file);
    if (payload.action === 'updateEarning') return updateEarning_(resources, payload.earning, payload.file);
    if (payload.action === 'deleteExpense') return deleteRecord_(resources.spreadsheet.getSheetByName('Expenses'), payload.id, 15);
    if (payload.action === 'deleteEarning') return deleteRecord_(resources.spreadsheet.getSheetByName('Earnings'), payload.id, 10);
    throw new Error('Unknown action');
  } catch (error) { return json_({ok:false, error:String(error.message || error)}); }
}
function getResources_() {
  const props = PropertiesService.getScriptProperties();
  let spreadsheetId = props.getProperty('SPREADSHEET_ID'), folderId = props.getProperty('FOLDER_ID'), spreadsheet, folder;
  if (spreadsheetId) spreadsheet = SpreadsheetApp.openById(spreadsheetId);
  else { spreadsheet = SpreadsheetApp.create('PhysiCode Finance Tracker'); props.setProperty('SPREADSHEET_ID', spreadsheet.getId()); const first=spreadsheet.getSheets()[0]; first.setName('Expenses'); setupSheet_(first,EXPENSE_HEADERS); setupSheet_(spreadsheet.insertSheet('Grants'),GRANT_HEADERS); }
  if (folderId) folder = DriveApp.getFolderById(folderId);
  else { folder=DriveApp.createFolder('PhysiCode Invoices & Receipts'); props.setProperty('FOLDER_ID',folder.getId()); }
  if (!spreadsheet.getSheetByName('Earnings')) setupSheet_(spreadsheet.insertSheet('Earnings'), EARNING_HEADERS);
  return {spreadsheet,folder};
}
function addGrant_(r,g) { r.spreadsheet.getSheetByName('Grants').appendRow([g.name,g.amount,g.status,g.notes||'',new Date()]); return json_({ok:true,spreadsheetUrl:r.spreadsheet.getUrl()}); }
function updateGrant_(r,g,oldName) { const s=r.spreadsheet.getSheetByName('Grants'),row=findTextRow_(s,oldName||g.name); if(!row)return addGrant_(r,g); s.getRange(row,1,1,5).setValues([[g.name,g.amount,g.status,g.notes||'',new Date()]]); if(oldName&&oldName!==g.name)replaceFundingSource_(r.spreadsheet.getSheetByName('Expenses'),oldName,g.name); return json_({ok:true,spreadsheetUrl:r.spreadsheet.getUrl()}); }
function deleteGrant_(r,name,reassign) { const s=r.spreadsheet.getSheetByName('Grants'),row=findTextRow_(s,name); if(row)s.deleteRow(row); if(reassign)replaceFundingSource_(r.spreadsheet.getSheetByName('Expenses'),name,'Company revenue'); return json_({ok:true,spreadsheetUrl:r.spreadsheet.getUrl()}); }
function findTextRow_(s,value) { if(!value||s.getLastRow()<2)return 0; const match=s.getRange(2,1,s.getLastRow()-1,1).createTextFinder(String(value)).matchEntireCell(true).findNext(); return match?match.getRow():0; }
function replaceFundingSource_(s,from,to) { if(!s||s.getLastRow()<2)return; const range=s.getRange(2,5,s.getLastRow()-1,1),values=range.getValues(); let changed=false; values.forEach(row=>{if(String(row[0])===String(from)){row[0]=to;changed=true;}}); if(changed)range.setValues(values); }
function addEarning_(r,e,u) { let fileUrl=''; if(u&&u.data){const blob=Utilities.newBlob(Utilities.base64Decode(u.data),u.type||'application/octet-stream',u.name||'document');fileUrl=r.folder.createFile(blob).getUrl();} r.spreadsheet.getSheetByName('Earnings').appendRow([e.id,e.dateISO,e.description,e.quantity,e.unitPrice,e.type,e.customer,e.amount,e.reference||'',fileUrl,new Date()]); return json_({ok:true,fileUrl,spreadsheetUrl:r.spreadsheet.getUrl()}); }
function updateExpense_(r,e,u) { const s=r.spreadsheet.getSheetByName('Expenses'),row=findRow_(s,e.id); if(!row) return addExpense_(r,e,u); let fileUrl=s.getRange(row,15).getValue(); if(u&&u.data){trashFile_(fileUrl);fileUrl=r.folder.createFile(Utilities.newBlob(Utilities.base64Decode(u.data),u.type||'application/octet-stream',u.name||'document')).getUrl();} s.getRange(row,1,1,16).setValues([[e.id,e.dateISO,e.description,e.category,e.grant,e.quantity,e.unitPrice,e.amount,e.payer,e.payerType,e.reimbursementStatus||'',e.dueDate||'',e.status,e.notes||'',fileUrl,new Date()]]); return json_({ok:true,fileUrl}); }
function updateEarning_(r,e,u) { const s=r.spreadsheet.getSheetByName('Earnings'),row=findRow_(s,e.id); if(!row) return addEarning_(r,e,u); let fileUrl=s.getRange(row,10).getValue(); if(u&&u.data){trashFile_(fileUrl);fileUrl=r.folder.createFile(Utilities.newBlob(Utilities.base64Decode(u.data),u.type||'application/octet-stream',u.name||'document')).getUrl();} s.getRange(row,1,1,11).setValues([[e.id,e.dateISO,e.description,e.quantity,e.unitPrice,e.type,e.customer,e.amount,e.reference||'',fileUrl,new Date()]]); return json_({ok:true,fileUrl}); }
function findRow_(s,id) { if(s.getLastRow()<2)return 0; const match=s.getRange(2,1,s.getLastRow()-1,1).createTextFinder(String(id)).matchEntireCell(true).findNext(); return match?match.getRow():0; }
function deleteRecord_(s,id,fileColumn) { const row=findRow_(s,id); if(row){trashFile_(s.getRange(row,fileColumn).getValue());s.deleteRow(row);} return json_({ok:true}); }
function trashFile_(url) { if(!url)return; const match=String(url).match(/[-\w]{25,}/); if(match)try{DriveApp.getFileById(match[0]).setTrashed(true);}catch(error){} }
function addExpense_(r,e,u) {
  let fileUrl=''; if(u&&u.data){const blob=Utilities.newBlob(Utilities.base64Decode(u.data),u.type||'application/octet-stream',u.name||'invoice');fileUrl=r.folder.createFile(blob).getUrl();}
  r.spreadsheet.getSheetByName('Expenses').appendRow([e.id,e.dateISO,e.description,e.category,e.grant,e.quantity,e.unitPrice,e.amount,e.payer,e.payerType,e.reimbursementStatus||'',e.dueDate||'',e.status,e.notes||'',fileUrl,new Date()]);
  return json_({ok:true,fileUrl,spreadsheetUrl:r.spreadsheet.getUrl(),folderUrl:r.folder.getUrl()});
}
function setupSheet_(s,h){s.getRange(1,1,1,h.length).setValues([h]).setFontWeight('bold').setBackground('#235d4a').setFontColor('#ffffff');s.setFrozenRows(1);s.autoResizeColumns(1,h.length);}
function json_(v){return ContentService.createTextOutput(JSON.stringify(v)).setMimeType(ContentService.MimeType.JSON);}
