document.addEventListener("DOMContentLoaded", function () {
    const body = document.body;
    const form = document.getElementById("teamForm");
    const submitButton =
        document.querySelector(".primary-btn") ||
        document.querySelector('button[type="submit"]');

    const textarea = document.getElementById("names");
    const quickMode = document.getElementById("quick_mode");
    const balancedMode = document.getElementById("balanced_mode");
    const modeSlider = document.querySelector(".mode-slider");
    const generatedHeading = document.querySelector(".generated-heading");

    const copyBtn = document.getElementById("copyResultsBtn");
    const csvBtn = document.getElementById("exportCsvBtn");
    const pdfBtn = document.getElementById("exportPdfBtn");

    const csvFileInput = document.getElementById("csv_file");
    const csvFileName = document.getElementById("csvFileName");

    function autoResizeTextarea() {
        if (!textarea) return;
        textarea.style.height = "auto";
        textarea.style.height = textarea.scrollHeight + "px";
    }

    function updateModeUI() {
        if (!quickMode || !balancedMode || !modeSlider || !textarea || !body) return;

        if (balancedMode.checked) {
            modeSlider.classList.add("right");
            body.classList.remove("theme-quick");
            body.classList.add("theme-balanced");
            textarea.placeholder = "John Doe-8, Jane Doe-5, Alex Smith-7, Sam Wilson-6";
        } else {
            modeSlider.classList.remove("right");
            body.classList.remove("theme-balanced");
            body.classList.add("theme-quick");
            textarea.placeholder = "John Doe, Jane Doe, Alex Smith, Sam Wilson";
        }
    }

    function getModeLabel() {
        if (body.classList.contains("theme-balanced")) {
            return "Balanced Mode";
        }
        return "Quick Mode";
    }

    function getTeamCards() {
        return document.querySelectorAll(".team-card");
    }

    function buildExportText() {
        const subtitle = document.querySelector(".subtitle")?.textContent?.trim() || "";
        const statCards = document.querySelectorAll(".stat-card");
        const teamCards = getTeamCards();

        let output = "IntelliTeam\n";
        if (subtitle) output += `${subtitle}\n`;
        output += `Mode: ${getModeLabel()}\n\n`;

        if (statCards.length > 0) {
            output += "SUMMARY\n";
            statCards.forEach((card) => {
                const value = card.querySelector(".stat-value")?.textContent?.trim() || "";
                const label = card.querySelector(".stat-label")?.textContent?.trim() || "";
                output += `${label}: ${value}\n`;
            });
            output += `\n`;
        }

        if (teamCards.length > 0) {
            output += "GENERATED TEAMS\n\n";

            teamCards.forEach((card, teamIndex) => {
                const teamName = card.querySelector(".team-name")?.textContent?.trim() || `Team ${teamIndex + 1}`;
                const memberCount = card.querySelector(".team-member-count")?.textContent?.trim() || "";
                const captain = card.querySelector(".captain-badge")?.textContent?.trim() || "";
                const teamRating = card.querySelector(".team-skill-pill")?.textContent?.trim() || "";

                output += `${teamName}\n`;
                if (memberCount) output += `${memberCount}\n`;
                if (captain) output += `${captain}\n`;
                if (teamRating) output += `${teamRating}\n`;

                const memberRows = card.querySelectorAll(".member-row");
                memberRows.forEach((row, index) => {
                    const memberName = row.querySelector(".member-name")?.textContent?.trim() || "";
                    const memberRating = row.querySelector(".member-rating-badge")?.textContent?.trim() || "";
                    let line = `${index + 1}. ${memberName}`;
                    if (memberRating) {
                        line += ` - Rating: ${memberRating}`;
                    }
                    output += `${line}\n`;
                });

                output += `\n`;
            });
        }

        return output.trim();
    }

    function buildExportCSV() {
        const isBalanced = body.classList.contains("theme-balanced");
        const teamCards = getTeamCards();

        if (!teamCards.length) {
            return "";
        }

        const rows = [];

        rows.push(["IntelliTeam Export"]);
        rows.push(["Mode", isBalanced ? "Balanced Mode" : "Quick Mode"]);
        rows.push([]);

        teamCards.forEach((card, teamIndex) => {
            const teamName = card.querySelector(".team-name")?.textContent?.trim() || `Team ${teamIndex + 1}`;

            const captainText = card.querySelector(".captain-badge")?.textContent?.trim() || "";
            const captain = captainText.replace("Captain:", "").trim();

            const teamRatingText = card.querySelector(".team-skill-pill")?.textContent?.trim() || "";
            const teamRating = teamRatingText.replace("Team Rating:", "").trim();

            rows.push(["Team Name", teamName]);
            rows.push(["Captain", captain]);

            if (isBalanced) {
                rows.push(["Team Rating", teamRating]);
                rows.push(["Member Number", "Member Name", "Member Rating"]);
            } else {
                rows.push(["Member Number", "Member Name"]);
            }

            const memberRows = card.querySelectorAll(".member-row");

            memberRows.forEach((row, index) => {
                const memberName = row.querySelector(".member-name")?.textContent?.trim() || "";

                if (isBalanced) {
                    const memberRating = row.querySelector(".member-rating-badge")?.textContent?.trim() || "";
                    rows.push([index + 1, memberName, memberRating]);
                } else {
                    rows.push([index + 1, memberName]);
                }
            });

            rows.push([]);
        });

        return rows
            .map(row =>
                row.map(value => `"${String(value ?? "").replace(/"/g, '""')}"`).join(",")
            )
            .join("\n");
    }

    function downloadFile(content, filename, type) {
        const blob = new Blob([content], { type });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");

        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        URL.revokeObjectURL(url);
    }

    if (textarea) {
        autoResizeTextarea();
        textarea.addEventListener("input", autoResizeTextarea);
    }

    if (quickMode) {
        quickMode.addEventListener("change", updateModeUI);
    }

    if (balancedMode) {
        balancedMode.addEventListener("change", updateModeUI);
    }

    const fileInput = document.getElementById("csv_file");
const fileName = document.getElementById("csvFileName");

if (fileInput && fileName) {
    fileInput.addEventListener("change", function () {
        if (fileInput.files.length > 0) {
            fileName.textContent = "✔ " + fileInput.files[0].name;
            fileName.style.color = "green";
        }
    });
}

    updateModeUI();

    if (csvFileInput && csvFileName) {
        csvFileInput.addEventListener("change", function () {
            if (csvFileInput.files.length > 0) {
                csvFileName.textContent = csvFileInput.files[0].name;
            } else {
                csvFileName.textContent = "No file chosen";
            }
        });
    }

    if (form && submitButton) {
        form.addEventListener("submit", function () {
            const originalText = submitButton.textContent.trim();
            submitButton.dataset.originalText = originalText;
            submitButton.innerHTML = `<span class="spinner"></span> Generating...`;
            submitButton.disabled = true;
        });
    }

    if (generatedHeading) {
        setTimeout(() => {
            generatedHeading.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });
        }, 250);
    }

    if (copyBtn) {
        copyBtn.addEventListener("click", async function () {
            try {
                const exportText = buildExportText();
                await navigator.clipboard.writeText(exportText);

                const originalText = copyBtn.textContent;
                copyBtn.textContent = "Copied!";

                setTimeout(() => {
                    copyBtn.textContent = originalText;
                }, 1200);
            } catch (error) {
                alert("Copy failed. Please try again.");
            }
        });
    }

    if (csvBtn) {
        csvBtn.addEventListener("click", function () {
            const csvContent = buildExportCSV();

            if (!csvContent) {
                alert("No teams available to export.");
                return;
            }

            const filename = body.classList.contains("theme-balanced")
                ? "intelliteam_balanced.csv"
                : "intelliteam_quick.csv";

            downloadFile(csvContent, filename, "text/csv;charset=utf-8;");
        });
    }

    if (pdfBtn) {
        pdfBtn.addEventListener("click", function () {
            const { jsPDF } = window.jspdf;
            const doc = new jsPDF();

            const pageWidth = doc.internal.pageSize.getWidth();
            const left = 15;
            const right = pageWidth - 15;
            const maxWidth = right - left;
            let y = 20;

            function addLine(text = "", size = 12, weight = "normal", gap = 8) {
                doc.setFont("helvetica", weight);
                doc.setFontSize(size);

                const lines = doc.splitTextToSize(text, maxWidth);

                if (y + (lines.length * gap) > 280) {
                    doc.addPage();
                    y = 20;
                }

                doc.text(lines, left, y);
                y += lines.length * gap;
            }

            const subtitle = document.querySelector(".subtitle")?.textContent?.trim() || "";
            const statCards = document.querySelectorAll(".stat-card");
            const teamCards = getTeamCards();

            addLine("IntelliTeam", 22, "bold", 10);
            if (subtitle) addLine(subtitle, 12, "normal", 8);
            addLine(`Mode: ${getModeLabel()}`, 11, "normal", 7);
            y += 4;

            if (statCards.length > 0) {
                addLine("SUMMARY", 15, "bold", 8);

                statCards.forEach((card) => {
                    const value = card.querySelector(".stat-value")?.textContent?.trim() || "";
                    const label = card.querySelector(".stat-label")?.textContent?.trim() || "";
                    addLine(`${label}: ${value}`, 11, "normal", 7);
                });

                y += 4;
            }

            if (teamCards.length > 0) {
                addLine("GENERATED TEAMS", 15, "bold", 8);

                teamCards.forEach((card, teamIndex) => {
                    const teamName = card.querySelector(".team-name")?.textContent?.trim() || `Team ${teamIndex + 1}`;
                    const memberCount = card.querySelector(".team-member-count")?.textContent?.trim() || "";
                    const captainText = card.querySelector(".captain-badge")?.textContent?.trim() || "";
                    const teamRatingText = card.querySelector(".team-skill-pill")?.textContent?.trim() || "";

                    addLine(teamName, 13, "bold", 8);
                    if (memberCount) addLine(memberCount, 11, "normal", 7);
                    if (captainText) addLine(captainText, 11, "normal", 7);
                    if (teamRatingText) addLine(teamRatingText, 11, "normal", 7);

                    const members = card.querySelectorAll(".member-row");
                    members.forEach((member, index) => {
                        const memberName = member.querySelector(".member-name")?.textContent?.trim() || "";
                        const memberRating = member.querySelector(".member-rating-badge")?.textContent?.trim() || "";

                        let line = `${index + 1}. ${memberName}`;
                        if (memberRating) {
                            line += ` (Rating: ${memberRating})`;
                        }

                        addLine(line, 11, "normal", 7);
                    });

                    y += 4;
                });
            }

            doc.save("intelliteam-output.pdf");
        });
    }
});