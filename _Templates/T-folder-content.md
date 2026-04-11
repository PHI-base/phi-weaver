

## 📁 Folder content: `= this.file.folder`
```dataview
table file.name as "Note", file.ctime as "Created"
where file.folder = this.file.folder and file.name != this.file.name
sort file.ctime desc
```
