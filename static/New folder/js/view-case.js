jQuery(document).ready(function ($) {

//   $('#event_date').datepicker({
//     "setDate": new Date(),
//     "autoclose": true
// });

$('#event_date').datetimepicker({
    format: 'dddd, MMMM DD, YYYY'
});

$('#event_time').datetimepicker({
  format: 'LT'
});


});
