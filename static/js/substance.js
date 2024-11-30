function renderDosageChart() {
    var ctx = document.getElementById('doseChart').getContext('2d');

    // Fetch dose data from formatted_dose
    var doseData = {{ substance.get('formatted_dose', {}) | tojson }};
    var roas = Object.keys(doseData);

    // Define dose levels and colors
    var doseLevels = ['Light', 'Common', 'Strong', 'Heavy'];
    var doseColors = {
        'Light': 'rgba(144, 238, 144, 1)',      // Light green
        'Common': 'rgba(255, 165, 0, 1)',       // Orange
        'Strong': 'rgba(255, 99, 71, 1)',       // Red-orange
        'Heavy': 'rgba(255, 69, 0, 1)'          // Dark red-orange
    };

    // Units and their multipliers to a base unit (e.g., mg)
    var unitMultipliers = {
        'g': 1000,
        'mg': 1,
        'μg': 0.001,
        'ug': 0.001,
        'µg': 0.001,
        'ml': 1  // Adjust as necessary for your context
    };

    // Prepare to store parsed data and dose segments
    var parsedDoseData = {};
    var roaSegments = {};
    var roaMinDose = {};
    var roaMaxDose = {};
    var overallMinDose = 0; // Start from zero
    var overallMaxDose = 0;
    var unitsUsed = new Set();

    // Helper function to parse dose values
    function parseDose(doseStr) {
        if (!doseStr || doseStr.toLowerCase() === 'no data') return null;

        // Regular expressions to match dose units and values
        var rangeRegex = /([\d\.]+)\s*(μg|ug|µg|mg|g|ml)?\s*-\s*([\d\.]+)\s*(μg|ug|µg|mg|g|ml)?\s*(\+)?/i;
        var singleValueRegex = /([\d\.]+)\s*(μg|ug|µg|mg|g|ml)?\s*(\+)?/i;

        var isOpenEnded = false;
        var low = null, high = null;
        var unit = 'mg'; // Default unit

        // Check for range values
        var match = doseStr.match(rangeRegex);
        if (match) {
            low = parseFloat(match[1]);
            var lowUnit = match[2] ? match[2].toLowerCase() : unit;
            high = parseFloat(match[3]);
            var highUnit = match[4] ? match[4].toLowerCase() : unit;
            unit = highUnit || lowUnit; // Prefer high unit, else low unit
            isOpenEnded = !!match[5];
        } else {
            // Check for single values
            match = doseStr.match(singleValueRegex);
            if (match) {
                low = parseFloat(match[1]);
                high = low;
                unit = match[2] ? match[2].toLowerCase() : unit;
                isOpenEnded = !!match[3];
            }
        }

        if (low === null || isNaN(low)) return null;

        unitsUsed.add(unit);

        return {
            low: low,
            high: high,
            unit: unit,
            isOpenEnded: isOpenEnded,
            display: doseStr.trim()
        };
    }

    // Step 1: Parse all doses and collect units used
    roas.forEach(function(roa) {
        parsedDoseData[roa] = {};
        doseLevels.forEach(function(level) {
            var doseStr = doseData[roa][level];
            var parsedDose = parseDose(doseStr);

            if (parsedDose) {
                parsedDoseData[roa][level] = parsedDose;
            } else {
                parsedDoseData[roa][level] = null;
            }
        });
    });

    // Step 2: Determine the unit to use for plotting
    var selectedUnit = null;
    var unitPriority = ['µg', 'μg', 'ug', 'mg', 'g', 'ml']; // Prioritize smaller units
    for (var i = 0; i < unitPriority.length; i++) {
        var unit = unitPriority[i];
        if (unitsUsed.has(unit)) {
            selectedUnit = unit;
            break;
        }
    }
    if (!selectedUnit) {
        selectedUnit = 'mg'; // Default to mg if no units are found
    }

    // Step 3: Convert all doses to the selected unit and update overall max dose
    roas.forEach(function(roa) {
        doseLevels.forEach(function(level) {
            var parsedDose = parsedDoseData[roa][level];

            if (parsedDose) {
                // Convert doses to the selected unit
                var multiplier = 1;
                var doseUnit = parsedDose.unit;
                if (unitMultipliers[doseUnit]) {
                    multiplier = unitMultipliers[doseUnit] / unitMultipliers[selectedUnit];
                } else {
                    // If the unit is unknown, assume multiplier is 1
                    multiplier = 1;
                }

                parsedDose.low *= multiplier;
                parsedDose.high *= multiplier;
                parsedDose.unit = selectedUnit; // Set unit to selectedUnit

                // Adjust for open-ended doses
                if (parsedDose.isOpenEnded) {
                    parsedDose.high += parsedDose.high * 0.25; // Extend by 25%
                }

                // Update max dose value
                overallMaxDose = Math.max(overallMaxDose, parsedDose.high);
            }
        });
    });

    // If no valid dose data is available, hide the chart and legend
    if (overallMaxDose === 0) {
        document.getElementById('doseChart').style.display = 'none';
        document.getElementById('doseLegend').style.display = 'none';
        var noDataMessage = document.createElement('p');
        noDataMessage.textContent = 'No dosage data available.';
        document.getElementById('doseChart').parentElement.appendChild(noDataMessage);
        return;
    }

    // Prepare data and segments for each ROA
    var validRoas = []; // Will hold the ROAs with valid data

    roas.forEach(function(roa) {
        var doseLevelsData = parsedDoseData[roa];
        var boundaries = new Set();

        // Collect all dose boundaries (low and high doses)
        doseLevels.forEach(function(level) {
            var dose = doseLevelsData[level];
            if (dose) {
                boundaries.add(dose.low);
                boundaries.add(dose.high);
            }
        });

        // Ensure zero is included for starting point
        boundaries.add(0);

        // Convert boundaries to array and sort
        var sortedBoundaries = Array.from(boundaries).sort(function(a, b) { return a - b; });

        if (sortedBoundaries.length < 2) {
            // Not enough data to create segments
            return;
        }

        // Build segments with associated dosage levels
        var segments = [];
        for (var i = 0; i < sortedBoundaries.length - 1; i++) {
            var startDose = sortedBoundaries[i];
            var endDose = sortedBoundaries[i + 1];

            // Determine the highest dosage level applicable in this segment
            var applicableLevels = doseLevels.filter(function(level) {
                var dose = doseLevelsData[level];
                if (dose) {
                    // For 'Light' level, adjust startDose to zero
                    var doseLow = level === 'Light' ? 0 : dose.low;
                    return startDose < dose.high && endDose > doseLow;
                }
                return false;
            });
            var highestLevel = applicableLevels[applicableLevels.length - 1]; // Last level is the highest

            if (highestLevel) {
                var dose = doseLevelsData[highestLevel];
                var isOpenEnded = dose.isOpenEnded && endDose >= dose.high;

                // For 'Light' dose, create a gradient from transparent to light green
                segments.push({
                    startDose: startDose,
                    endDose: endDose,
                    doseLevel: highestLevel,
                    isOpenEnded: isOpenEnded,
                    isLight: highestLevel === 'Light'
                });
            }
        }

        if (segments.length > 0) {
            roaSegments[roa] = segments;

            // Store min and max doses for this ROA
            roaMinDose[roa] = 0; // Start from zero
            roaMaxDose[roa] = segments[segments.length - 1].endDose;

            validRoas.push(roa);
        }
    });

    // Prepare data for the chart using valid RoAs
    var data = validRoas.map(function(roa) {
        return [roaMinDose[roa], roaMaxDose[roa]];
    });

    // Configure the chart
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: validRoas,
            datasets: [{
                label: 'Dosage',
                data: data,
                backgroundColor: function(context) {
                    var index = context.dataIndex;
                    var chart = context.chart;
                    var xScale = chart.scales.x;
                    var ctx = chart.ctx;

                    var roa = validRoas[index];
                    var segments = roaSegments[roa];
                    if (!segments || segments.length === 0) {
                        return 'rgba(0,0,0,0)'; // Transparent
                    }

                    // Get the pixel positions for start and end of the bar
                    var barStartValue = roaMinDose[roa];
                    var barEndValue = roaMaxDose[roa];

                    if (barStartValue === undefined || barEndValue === undefined || isNaN(barStartValue) || isNaN(barEndValue)) {
                        return 'rgba(0,0,0,0)'; // Transparent
                    }

                    var barStartPixel = xScale.getPixelForValue(barStartValue);
                    var barEndPixel = xScale.getPixelForValue(barEndValue);

                    if (!isFinite(barStartPixel) || !isFinite(barEndPixel)) {
                        return 'rgba(0,0,0,0)'; // Transparent
                    }

                    // Create gradient from barStartPixel to barEndPixel
                    var gradient = ctx.createLinearGradient(barStartPixel, 0, barEndPixel, 0);

                    var totalDoseRange = barEndValue - barStartValue;

                    segments.forEach(function(segment) {
                        var startPos = (segment.startDose - barStartValue) / totalDoseRange;
                        var endPos = (segment.endDose - barStartValue) / totalDoseRange;

                        var color = doseColors[segment.doseLevel];

                        // Clamp positions between 0 and 1
                        startPos = Math.max(0, Math.min(1, startPos));
                        endPos = Math.max(0, Math.min(1, endPos));

                        if (segment.isLight && segment.startDose === 0) {
                            // For 'Light' dose starting at zero, fade from transparent to light green
                            gradient.addColorStop(0, 'rgba(144, 238, 144, 0)'); // Transparent
                            gradient.addColorStop(endPos, color);
                        } else if (segment.isOpenEnded) {
                            // For open-ended segments, fade out to transparent
                            var midPos = (startPos + endPos) / 2;
                            gradient.addColorStop(startPos, color);
                            gradient.addColorStop(midPos, color);
                            gradient.addColorStop(endPos, 'rgba(255,255,255,0)'); // Fade to transparent
                        } else {
                            gradient.addColorStop(startPos, color);
                            gradient.addColorStop(endPos, color);
                        }
                    });

                    return gradient;
                },
                borderWidth: 0,
                barThickness: 'flex',
                maxBarThickness: 30,
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    type: 'linear',
                    min: 0, // Start from zero
                    max: overallMaxDose + (overallMaxDose * 0.05),
                    title: {
                        display: true,
                        text: 'Dose (' + selectedUnit + ')'
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        display: false
                    },
                    barPercentage: validRoas.length === 1 ? 0.5 : 0.8,
                    categoryPercentage: validRoas.length === 1 ? 0.8 : 0.9,
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(tooltipItem) {
                            var index = tooltipItem.dataIndex;
                            var roa = validRoas[index];
                            var segments = roaSegments[roa];
                            if (segments && segments.length > 0) {
                                var label = roa + ':';
                                segments.forEach(function(segment) {
                                    var doseLevel = segment.doseLevel;
                                    var doseLevelData = parsedDoseData[roa][doseLevel];
                                    label += '\n' + doseLevel + ': ' + doseLevelData.display;
                                });
                                return label;
                            } else {
                                return roa + ': No data';
                            }
                        }
                    }
                },
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                        generateLabels: function(chart) {
                            return doseLevels.map(function(level) {
                                return {
                                    text: level,
                                    fillStyle: doseColors[level],
                                    strokeStyle: doseColors[level],
                                    lineWidth: 0,
                                    hidden: false
                                };
                            });
                        }
                    }
                }
            },
            layout: {
                padding: {
                    top: 10,
                    bottom: 10
                }
            }
        }
    });

    // Render the dosage table
    renderDosageTable();

    function renderDosageTable() {
        var doseTableHead = document.getElementById('doseTableHead');
        var doseTableBody = document.getElementById('doseTableBody');

        // Clear existing table content
        doseTableHead.innerHTML = '';
        doseTableBody.innerHTML = '';

        // Create table headers
        var headerRow = document.createElement('tr');
        var roaHeader = document.createElement('th');
        roaHeader.textContent = 'ROA';
        headerRow.appendChild(roaHeader);

        doseLevels.forEach(function(level) {
            var th = document.createElement('th');
            th.textContent = level;
            headerRow.appendChild(th);
        });
        doseTableHead.appendChild(headerRow);

        // Create table rows
        validRoas.forEach(function(roa) {
            var row = document.createElement('tr');
            var roaCell = document.createElement('td');
            roaCell.textContent = roa;
            row.appendChild(roaCell);

            doseLevels.forEach(function(level) {
                var dose = parsedDoseData[roa][level];
                var cell = document.createElement('td');
                cell.style.backgroundColor = doseColors[level];
                cell.style.color = 'black';
                cell.style.padding = '5px';
                cell.style.textAlign = 'center';

                if (dose) {
                    cell.textContent = dose.display;
                } else {
                    cell.textContent = 'No data';
                    cell.style.backgroundColor = '#f0f0f0';
                }
                row.appendChild(cell);
            });
            doseTableBody.appendChild(row);
        });
    }
}

// Call the renderDosageChart function when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    renderDosageChart();
});