
document.addEventListener("DOMContentLoaded", function () {
    const body = document.body;
    const form = document.getElementById("teamForm");
    const submitButton =
        document.querySelector(".primary-btn") ||
        document.querySelector('button[type="submit"]');

    const textarea = document.getElementById("names");
    const teamCountInput = document.getElementById("team_count");

    const quickMode = document.getElementById("quick_mode");
    const balancedMode = document.getElementById("balanced_mode");
    const modeSlider = document.querySelector(".mode-slider");

    const generatedHeading = document.querySelector(".generated-heading");

    const copyBtn = document.getElementById("copyResultsBtn");
    const csvBtn = document.getElementById("exportCsvBtn");
    const pdfBtn = document.getElementById("exportPdfBtn");

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
            textarea.placeholder = "Ali-8, Sara-5, John-7";
        } else {
            modeSlider.classList.remove("right");
            body.classList.remove("theme-balanced");
            body.classList.add("theme-quick");
            textarea.placeholder = "Ali, Sara, John, Fatima";
        }
    }

    function buildExportText() {
        const title = document.querySelector(".title")?.textContent?.trim() || "IntelliTeam";
        const subtitle = document.querySelector(".subtitle")?.textContent?.trim() || "";

        const statCards = document.querySelectorAll(".stat-card");
        const teamCards = document.querySelectorAll(".team-card");

        let output = `${title}\n`;
        if (subtitle) output += `${subtitle}\n`;
        output += `\n`;

        if (statCards.length > 0) {
            output += `SUMMARY\n`;
            statCards.forEach((card) => {
                const value = card.querySelector(".stat-value")?.textContent?.trim() || "";
                const label = card.querySelector(".stat-label")?.textContent?.trim() || "";
                output += `${label}: ${value}\n`;
            });
            output += `\n`;
        }

        if (teamCards.length > 0) {
            output += `GENERATED TEAMS\n\n`;

            teamCards.forEach((card) => {
                const teamName = card.querySelector(".team-name")?.textContent?.trim() || "Team";
                const memberCount = card.querySelector(".team-member-count")?.textContent?.trim() || "";
                const captain = card.querySelector(".captain-badge")?.textContent?.trim() || "";
                const teamRating = card.querySelector(".team-skill-pill")?.textContent?.trim() || "";

                output += `${teamName}\n`;
                if (memberCount) output += `${memberCount}\n`;
                if (captain) output += `${captain}\n`;
                if (teamRating) output += `${teamRating}\n`;

                const members = card.querySelectorAll(".member-row");
                members.forEach((member, index) => {
                    const text = member.textContent.replace(/\s+/g, " ").trim();
                    output += `${index + 1}. ${text}\n`;
                });

                output += `\n`;
            });
        }

        return output.trim();
    }

    function buildExportCSV() {
        const teamCards = document.querySelectorAll(".team-card");
        let rows = [["Team Name", "Captain", "Team Rating", "Member Number", "Member Name", "Rating"]];

        teamCards.forEach((card) => {
            const teamName = card.querySelector(".team-name")?.textContent?.trim() || "";
            const captainText = card.querySelector(".captain-badge")?.textContent?.trim() || "";
            const teamRatingText = card.querySelector(".team-skill-pill")?.textContent?.trim() || "";

            const captain = captainText.replace(/^Captain:\s*/i, "").trim();
            const teamRating = teamRatingText.replace(/^Team Rating:\s*/i, "").trim();

            const members = card.querySelectorAll(".member-row");

            members.forEach((member, index) => {
                const memberNameEl = member.querySelector(".member-name");
                const memberRatingEl = member.querySelector(".member-rating");

                const memberName = memberNameEl ? memberNameEl.textContent.trim() : member.textContent.trim();
                const memberRating = memberRatingEl
                    ? memberRatingEl.textContent.replace(/^Rating:\s*/i, "").trim()
                    : "";

                rows.push([
                    teamName,
                    captain,
                    teamRating,
                    index + 1,
                    memberName,
                    memberRating
                ]);
            });
        });

        return rows
            .map((row) =>
                row
                    .map((cell) => `"${String(cell).replace(/"/g, '""')}"`)
                    .join(",")
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

    updateModeUI();

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
            downloadFile(csvContent, "intelliteam-output.csv", "text/csv;charset=utf-8;");
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

            const title = document.querySelector(".title")?.textContent?.trim() || "IntelliTeam";
            const subtitle = document.querySelector(".subtitle")?.textContent?.trim() || "";
            const statCards = document.querySelectorAll(".stat-card");
            const teamCards = document.querySelectorAll(".team-card");

            addLine(title, 22, "bold", 10);
            if (subtitle) addLine(subtitle, 12, "normal", 8);
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