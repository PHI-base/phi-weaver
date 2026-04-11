<%* // Get the 1st January next year 
let firstJanNextYear = moment(tp.file.title,'YYYY-MM-DD').endOf('year').add(1, 'days'); 
//Get today 
let today = moment(); 
// difference between 1st Jan. next year and today 
let diff = firstJanNextYear.diff(today, 'days'); -%> 

days_till_2024: <% diff %>
