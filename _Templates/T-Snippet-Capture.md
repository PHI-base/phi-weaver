<%*
// Configure filepath
let now = new Date();
let year = now.getFullYear();
let month = String(now.getMonth() + 1).padStart(2, '0');
let day = String(now.getDate()).padStart(2, '0');
let hours = String(now.getHours()).padStart(2, '0');
let minutes = String(now.getMinutes()).padStart(2, '0');

const fileName = await tp.system.prompt("Snippet Title", "", true);
const popularLanguages = ["javascript", "python", "java",  "css", "html", "markdown", "bash", "bat", "sbash", "sql"];
const langName = await tp.system.suggester(popularLanguages, popularLanguages, true, "Choose Language");
const codeSnippet = await tp.system.prompt("Snippet", "", false, true);
const tagsInput = await tp.system.prompt("Enter Tags");
const folderPath = "Snippets/" + langName;
let tagsArray = ["snippet", langName]; // Initialize with 'snippet' and the language as the first elements

if (tagsInput) {
    const additionalTags = tagsInput.split(/,|;|\s+/).map(tag => tag.trim()).filter(tag => tag.length > 0);
    tagsArray = tagsArray.concat(additionalTags); // Add additional tags to the array
}

let folder = app.vault.getAbstractFileByPath(folderPath);

if (folder === null) {
    await app.vault.createFolder(folderPath);
    folder = app.vault.getAbstractFileByPath(folderPath);
}

let newFilePath = `${folderPath}/${fileName}.md`;

// Create an empty file
await app.vault.create(newFilePath, ""); 

let newFile = app.vault.getAbstractFileByPath(newFilePath);

// Configure frontmatter
await app.fileManager.processFrontMatter(newFile, (frontmatter) => {
  frontmatter["Subject"] = fileName;
  frontmatter["Language"] = langName;
  frontmatter["Date"] = tp.date.now();
  frontmatter["Time"] = hours + ":" + minutes;
  frontmatter["Tags"] = tagsArray.join(", "); 
});

const content = `\`\`\`${langName}
${codeSnippet}
\`\`\``;

// Append content
await app.vault.append(newFile, content);
await app.workspace.activeLeaf.openFile(newFile);
%>