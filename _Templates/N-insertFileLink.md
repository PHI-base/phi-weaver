
<%* 
  const userInput = await tp.system.prompt("Enter the rest of the filename:");
  const newFileName = tp.date.now("YYYY-MM-DD") + " " + userInput;
  const newFile = await tp.file.create_new(tp.file.find_tfile("T-testMU"), newFileName, false);
  tR = "[[" + newFile.basename + "]]";
%>

