---
date: '[[<%tp.date.now("YYYY-MM-DD")%>]]'
modified: []
---

<<[[<%tp.date.now("YYYY-MM-DD",-1)%>]] - [[<%tp.date.now("YYYY-MM-DD",1)%>]]>>

# TODAY'S NOTES:

## To do today:


Links: Facility-logs, check OUTLOOK tasks!
[[phibase-tasks]]
Link to [B63-Teams-channel- Facilities](https://teams.microsoft.com/l/channel/19%3A-eJMUlzePuJio_E7enJy8YEQgVHf8tF7j0oYMictctQ1%40thread.tacv2/General?groupId=0f5a19dc-6009-4ce6-8d21-e2530b68a74c&tenantId=b6883625-8941-4342-b0e3-7b8cc8392f64)


# EXPERIMENTS-ACTIVE
```dataview
TABLE Title, StartDate as "Start date"
FROM ("01-EXPERIMENTS")
WHERE Completed != true
```


> [!example] Today's Notes
```dataview
table without id
file.link as Note,
file.folder as Folder,
file.mtime as "Last Modified"
FROM -"Dailies"
where file.mtime > (date(now) - dur(12 hours))
sort file.mtime desc
```
