function uploadFiles() {
    let files = $("#fileInput")[0].files;
    let formData = new FormData();

    for (let i = 0; i < files.length; i++) {
        formData.append("files", files[i]);
    }

    $("#uploadMessage").html("Uploading file... ⏳");

    $.ajax({
        url: "/upload",
        type: "POST",
        data: formData,
        contentType: false,
        processData: false,
        success: function(response) {
            if (response.success) {
                $("#uploadMessage").html("✅ Files uploaded successfully!");
                displayPreview(response.preview);
            } else {
                $("#uploadMessage").html("❌ Error: " + response.error);
            }
        },
        error: function(xhr, status, error) {
            console.log(xhr.responseText);
            $("#uploadMessage").html("❌ Upload failed! Check console for details.");
        }
    });
}

function displayPreview(data) {
    let table = $("#previewTable");
    table.empty();

    if (data.length === 0) {
        table.append("<tr><td>No data found</td></tr>");
        return;
    }

    let headers = ["Vehicle Number", "Total Price", "Station", "Date"];

    let headerRow = "<tr>";
    headers.forEach(header => {
        headerRow += `<th>${header}</th>`;
    });
    headerRow += "</tr>";
    table.append(headerRow);

    data.forEach(row => {
        let rowHTML = "<tr>";
        headers.forEach(header => {
            rowHTML += `<td>${row[header] || "N/A"}</td>`;
        });
        rowHTML += "</tr>";
        table.append(rowHTML);
    });

    $("#previewTable").DataTable();
}

function applyFilter() {
    let filterVehicle = $("#filterVehicle").val().trim();

    if (!filterVehicle) {
        alert("⚠️ Please enter a Vehicle Number.");
        return;
    }

    $.ajax({
        url: "/filter",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({
            filters: { "Vehicle Number": filterVehicle }
        }),
        success: function (response) {
            if (response.success) {
                displayFilteredData(response.filtered_data);
                $("#summaryBox").show();
                $("#totalPriceSummary").text(response.total_price.toFixed(2));
                $("#totalRecordsSummary").text(response.filtered_data.length);
            } else {
                alert("❌ Error: " + response.error);
                $("#summaryBox").hide();
            }
        },
        error: function() {
            alert("❌ Something went wrong while filtering data.");
            $("#summaryBox").hide();
        }
    });
}

function displayFilteredData(data) {
    let table = $("#filteredTable");

    // // ✅ Destroy existing DataTable if exists
    // if ( $.fn.DataTable.isDataTable("#filteredTable") ) {
    //     table.DataTable().destroy();
    // }

    table.empty();

    if (data.length === 0) {
        table.append("<tr><td colspan='4'>No data found</td></tr>");
        return;
    }

    let headers = ["Vehicle Number", "Total Price", "Station", "Date"];

    let headerRow = "<tr>";
    headers.forEach(header => {
        headerRow += `<th>${header}</th>`;
    });
    headerRow += "</tr>";
    table.append(headerRow);

    let totalPrice = 0;

    data.forEach(row => {
        let rowHTML = "<tr>";
        headers.forEach(header => {
            rowHTML += `<td>${row[header] || "N/A"}</td>`;
        });
        rowHTML += "</tr>";

        totalPrice += parseFloat(row["Total Price"]) || 0;
        table.append(rowHTML);
    });

    let totalRow = `<tr style="font-weight:bold;">
        <td colspan="1">Total</td>
        <td>${totalPrice.toFixed(2)}</td>
        <td colspan="2"></td>
    </tr>`;
    table.append(totalRow);

    $("#filteredTable").DataTable();
}

function downloadCSV() {
    let filterVehicle = $("#filterVehicle").val().trim();

    if (!filterVehicle) {
        alert("⚠️ Please enter a Vehicle Number before downloading.");
        return;
    }

    window.location.href = `/download?vehicle=${encodeURIComponent(filterVehicle)}`;
}