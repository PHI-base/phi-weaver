function returnStudyOptions (tp, timeAvailable) {
    let totalTimeRequired = 0;
    const types = ['audiobook', 'course'];
    let result = "";

    types.forEach(type => {
        result += `### ${type}:\n\n`;
        const options = app.plugins.plugins.dataview.api
        .pages(`"study-materials/${type}"`)
        .where(page => {
            totalTimeRequired += page.time_required;
            if(totalTimeRequired <= timeAvailable) {
                return true;
            }
            else {
                totalTimeRequired -= page.time_required;
                return false;
            }
        })
    
        options.forEach((option) => {
            result += `- ${option.file.link}: ${option.time_required}\n\n`
        })
        totalTimeRequired = 0;
    })
    
    return result
}
module.exports = returnStudyOptions;