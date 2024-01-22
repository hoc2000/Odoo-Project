
$(document).ready(function () {
    // Your JavaScript code goes here
    // Example: Attach an event listener to an input field
    $("#project_id").on('change', function () {
        var selectedValue = $(this).val();
        // Make an AJAX request to fetch options for Selector 2 based on selectedValue
        $.ajax({
            type: "POST",
            url: "/my/get_options",
            dataType: "json",
            data: {
                project_value: selectedValue,
            },
            success: function (res) {
                // Update options for Selector 2 based on the response
                console.log(res);
                var fieldSelection2 = $('#product');
                fieldSelection2.empty();
                _.each(res, function (option) {
                    var optionElement = $('<option>').val(option.value).text(option.text);
                    fieldSelection2.append(optionElement);
                });
            },
        });
    });
});