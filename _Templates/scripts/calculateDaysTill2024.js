
function calculateDaysTill2024() { 
// Get the 1st January next year 
const today = moment();
let firstJanNextYear = moment(today).endOf('year').add(1, 'day'); 
// Difference between 1st Jan. next year and today
let diff = firstJanNextYear.diff(today, 'days'); 
return diff; 
}

module.exports = calculateDaysTill2024;