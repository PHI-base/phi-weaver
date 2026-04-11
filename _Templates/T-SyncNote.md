<%*
let now = new Date();
let year = now.getFullYear();
let month = String(now.getMonth() + 1).padStart(2, '0');
let day = String(now.getDate()).padStart(2, '0');
let hours = String(now.getHours()).padStart(2, '0');
let minutes = String(now.getMinutes()).padStart(2, '0');

const personName = tp.file.selection();
const templatePath = tp.file.find_tfile("T-FillSyncNote")
const folderPath = "0️⃣ Meetings/" + personName;
let folder = app.vault.getAbstractFileByPath(folderPath);

if (folder === null) {
    await app.vault.createFolder(folderPath);
    // get the folder again after creation
    folder = app.vault.getAbstractFileByPath(folderPath);
}
tp.file.create_new(templatePath, personName + ` ${year}-${month}-${day} ${hours}${minutes}`, false, folder)
%>[[<% personName + ` ${year}-${month}-${day} ${hours}${minutes}` %>]]

