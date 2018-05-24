$(document).ready(function () {

	function numberToMoney(numberToFormat) {
	    var numberToFormat = numberToFormat.toFixed(2).split('.');
	    numberToFormat[0] = "R$ " + numberToFormat[0].split(/(?=(?:...)*$)/).join('.');
	    return numberToFormat.join(',');
	}

	var sumTotalCost = 0;
	$("[name='total-cost']").each(function() {
	    var valueCost = $(this).text();
	    sumTotalCost += parseFloat(valueCost);
	});
	$('#campaign-total').html(numberToMoney(sumTotalCost));

	var sumExpectedRevenue = 0;
	$("[name='expected-revenue']").each(function() {
	    var valueRevenue = $(this).text();
	    sumExpectedRevenue += parseFloat(valueRevenue);
	});

	$('#expected-revenue').html(numberToMoney(sumExpectedRevenue));
});
