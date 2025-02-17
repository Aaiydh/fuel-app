function uploadFile() {
    let file = $("#fileInput")[0].files[0];
    let formData = new FormData();
    formData.append("file", file);

    $("#uploadMessage").html("Uploading file... ⏳");

    $.ajax({
        url: "/upload",
        type: "POST",
        data: formData,
        contentType: false,
        processData: false,
        success: function(response) {
            if (response.success) {
                $("#uploadMessage").html("✅ File uploaded successfully!");
                displayPreview(response.preview);
            } else {
                $("#uploadMessage").html("❌ Error: " + response.error);
            }
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

    let headers = Object.keys(data[0]);
    let headerRow = "<tr>";
    headers.forEach(header => {
        headerRow += `<th>${header}</th>`;
    });
    headerRow += "</tr>";
    table.append(headerRow);

    data.forEach(row => {
        let rowHTML = "<tr>";
        headers.forEach(header => {
            rowHTML += `<td>${row[header]}</td>`;
        });
        rowHTML += "</tr>";
        table.append(rowHTML);
    });

    $("#previewTable").DataTable();
}

function applyFilter() {
    let filterVehicle = $("#filterVehicle").val().trim();
    let filterDate = $("#filterDate").val().trim();
    let filterStation = $("#filterStation").val().trim();

    if (filterVehicle === "" && filterDate === "" && filterStation === "") {
        alert("⚠️ Please enter at least one filter value.");
        return;
    }

    let filename = $("#fileInput")[0].files[0] ? $("#fileInput")[0].files[0].name : null;

    if (!filename) {
        alert("⚠️ No uploaded file detected. Please upload an Excel file first.");
        return;
    }

    $.ajax({
        url: "/filter",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({
            filename: filename,
            filters: {
                "Vehicle Number": filterVehicle,
                "Date": filterDate,
                "Station": filterStation
            }
        }),
        success: function(response) {
            if (response.success) {
                displayFilteredData(response.filtered_data);
            } else {
                alert("❌ Error: " + response.error);
            }
        },
        error: function() {
            alert("❌ Something went wrong while filtering data.");
        }
    });
}

function displayFilteredData(data) {
    let table = $("#filteredTable");
    table.empty();

    if (data.length === 0) {
        table.append("<tr><td>No data found</td></tr>");
        return;
    }

    let headers = Object.keys(data[0]);
    let headerRow = "<tr>";
    headers.forEach(header => {
        headerRow += `<th>${header}</th>`;
    });
    headerRow += "</tr>";
    table.append(headerRow);

    data.forEach(row => {
        let rowHTML = "<tr>";
        headers.forEach(header => {
            rowHTML += `<td>${row[header]}</td>`;
        });
        rowHTML += "</tr>";
        table.append(rowHTML);
    });

    $("#filteredTable").DataTable();
}


function downloadCSV() {
    window.location.href = "/download";
}
