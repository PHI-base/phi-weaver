<%* 
const filename = tp.file.selection() 
const folder = app.vault.getAbstractFileByPath("Tasks") 
tp.file.create_new("", filename, false, folder) 
%>[[<% filename %>]]