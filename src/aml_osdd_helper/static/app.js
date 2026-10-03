const form =
    document.getElementById("analysisForm");


const loading =
    document.getElementById("loading");


const results =
    document.getElementById("results");


const errorBox =
    document.getElementById("errorBox");


const button =
    document.getElementById("analyzeButton");


const buttonText =
    document.getElementById("buttonText");


const loadingText =
    document.getElementById("loadingText");


/* =========================================
   HELPERS
========================================= */

const sleep = (ms) =>
    new Promise(resolve => setTimeout(resolve, ms));


function escapeHtml(value) {

    if (
        value === null ||
        value === undefined
    ) {
        return "";
    }

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


/* =========================================
   LOADING
========================================= */

function showLoading() {

    loading.classList.remove("hidden");

    results.classList.add("hidden");

    errorBox.classList.add("hidden");

    button.disabled = true;

    buttonText.innerHTML = `
        <span class="animate-spin">
            ◌
        </span>

        ANALYZING...
    `;


    const messages = [

        "Searching public sources...",

        "Extracting intelligence...",

        "Processing source documents...",

        "Summarizing evidence...",

        "Analyzing entity information...",

        "Checking adverse media...",

        "Building risk assessment..."

    ];


    let index = 0;


    loadingText.textContent =
        messages[0];


    window.loadingInterval =
        setInterval(() => {

            index =
                (index + 1) %
                messages.length;

            loadingText.textContent =
                messages[index];

        }, 2500);
}


function hideLoading() {

    clearInterval(
        window.loadingInterval
    );

    loading.classList.add("hidden");

    button.disabled = false;

    buttonText.innerHTML = `
        <span>✦</span>
        RUN OSDD ANALYSIS
    `;
}


function showError(message) {

    errorBox.classList.remove("hidden");

    document.getElementById(
        "errorMessage"
    ).textContent = message;
}


/* =========================================
   RISK COLORS
========================================= */


/*
    Exactly 10 colors.

    1  = Green
    2  = Green
    3  = Teal
    4  = Yellow
    5  = Yellow
    6  = Orange
    7  = Orange
    8  = Red Orange
    9  = Red
    10 = Deep Red
*/

const RISK_COLORS = [

    "#22c55e", // 1
    "#34d399", // 2
    "#2dd4bf", // 3
    "#a3e635", // 4
    "#facc15", // 5
    "#f59e0b", // 6
    "#fb923c", // 7
    "#f97316", // 8
    "#ef4444", // 9
    "#dc2626"  // 10

];


/* =========================================
   RISK LEVEL FALLBACK
========================================= */

function getRiskLabel(score) {

    if (score <= 2) {
        return "Very Low";
    }

    if (score <= 4) {
        return "Low";
    }

    if (score <= 6) {
        return "Moderate";
    }

    if (score <= 8) {
        return "High";
    }

    return "Critical";
}


function getRiskColor(score) {

    return RISK_COLORS[
        Math.max(
            0,
            Math.min(
                9,
                score - 1
            )
        )
    ];
}


/* =========================================
   SVG GEOMETRY
========================================= */


/*
    Convert polar coordinates
    into Cartesian coordinates.
*/

function polarToCartesian(
    cx,
    cy,
    radius,
    angle
) {

    const radians =
        (angle - 90) *
        Math.PI /
        180;

    return {

        x:
            cx +
            radius *
            Math.cos(radians),

        y:
            cy +
            radius *
            Math.sin(radians)

    };
}


/*
    Create an annular sector.

    This creates the individual
    "boxed pie" segments.
*/

function createArcPath(
    cx,
    cy,
    outerRadius,
    innerRadius,
    startAngle,
    endAngle
) {

    const outerStart =
        polarToCartesian(
            cx,
            cy,
            outerRadius,
            startAngle
        );


    const outerEnd =
        polarToCartesian(
            cx,
            cy,
            outerRadius,
            endAngle
        );


    const innerStart =
        polarToCartesian(
            cx,
            cy,
            innerRadius,
            startAngle
        );


    const innerEnd =
        polarToCartesian(
            cx,
            cy,
            innerRadius,
            endAngle
        );


    const largeArcFlag =
        endAngle - startAngle <= 180
            ? "0"
            : "1";


    return [

        "M",
        outerStart.x,
        outerStart.y,

        "A",
        outerRadius,
        outerRadius,
        0,
        largeArcFlag,
        1,
        outerEnd.x,
        outerEnd.y,

        "L",
        innerEnd.x,
        innerEnd.y,

        "A",
        innerRadius,
        innerRadius,
        0,
        largeArcFlag,
        0,
        innerStart.x,
        innerStart.y,

        "Z"

    ].join(" ");
}


/* =========================================
   CREATE METER
========================================= */

function createRiskMeter(score) {

    const container =
        document.getElementById(
            "riskSegments"
        );


    container.innerHTML = "";


    /*
        10 segments.

        Semicircle:
        180° → 360°
    */

    const totalSegments = 10;

    const gap = 2.5;

    const segmentAngle =
        180 / totalSegments;


    for (
        let i = 0;
        i < totalSegments;
        i++
    ) {

        const startAngle =
            270 +
            i * segmentAngle +
            gap;


        const endAngle =
            270 +
            (i + 1) *
            segmentAngle -
            gap;


        const path =
            document.createElementNS(
                "http://www.w3.org/2000/svg",
                "path"
            );


        path.setAttribute(
            "d",
            createArcPath(
                160,
                130,
                112,
                70,
                startAngle,
                endAngle
            )
        );


        path.setAttribute(
            "fill",
            RISK_COLORS[i]
        );


        path.setAttribute(
            "class",
            "risk-segment"
        );


        /*
            Activate according to score.
        */

        if (i < score) {

            path.classList.add(
                "active"
            );

        } else {

            path.classList.add(
                "inactive"
            );

        }


        /*
            Give each segment its own
            CSS color for glow.
        */

        path.style.color =
            RISK_COLORS[i];


        container.appendChild(path);

    }


    /*
        Position needle.

        Score 1:
            far left

        Score 10:
            far right
    */

    const needle =
        document.getElementById(
            "riskNeedle"
        );


    const percentage =
        (score - 1) /
        9;


    const angle =
        -90 +
        percentage * 180;


    needle.style.transform =
        `rotate(${angle}deg)`;


    /*
        Color needle according
        to current risk.
    */

    const color =
        getRiskColor(score);


    needle.querySelector(
        "line"
    ).style.stroke = color;


    needle.querySelector(
        "circle:first-of-type"
    ).style.fill = color;

}


/* =========================================
   SCORE ANIMATION
========================================= */

function animateScore(
    element,
    target
) {

    const duration = 1000;

    const start =
        performance.now();


    function update(now) {

        const progress =
            Math.min(
                (now - start) /
                duration,
                1
            );


        const eased =
            1 -
            Math.pow(
                1 - progress,
                3
            );


        const current =
            Math.round(
                target * eased
            );


        element.textContent =
            current;


        if (progress < 1) {

            requestAnimationFrame(
                update
            );

        }

    }


    requestAnimationFrame(update);
}


/* =========================================
   RENDER RISK
========================================= */

function renderRisk(result) {

    /*
        The application now uses
        a 1–10 risk scale.

        If an old backend accidentally
        returns 0–100, convert it.
    */

    let score =
        Number(
            result.risk_score
        );


    if (!Number.isFinite(score)) {
        score = 1;
    }


    /*
        Backwards compatibility.

        If your old backend is still
        returning 0–100:
    */

    if (score > 10) {

        score =
            Math.round(
                score / 10
            );

    }


    score =
        Math.max(
            1,
            Math.min(
                10,
                Math.round(score)
            )
        );


    const scoreElement =
        document.getElementById(
            "riskScore"
        );


    const levelElement =
        document.getElementById(
            "riskLevel"
        );


    const confidenceElement =
        document.getElementById(
            "confidence"
        );


    const color =
        getRiskColor(score);


    /*
        Use backend risk level
        when available.
    */

    const riskLevel =
        result.risk_level ||
        getRiskLabel(score);


    scoreElement.style.color =
        color;


    levelElement.style.color =
        color;


    levelElement.textContent =
        riskLevel;


    confidenceElement.textContent =
        `${Math.round(
            Number(
                result.confidence || 0
            ) * 100
        )}%`;


    /*
        Build the segmented meter.
    */

    createRiskMeter(score);


    /*
        Animate the number.
    */

    scoreElement.textContent = "0";


    setTimeout(() => {

        animateScore(
            scoreElement,
            score
        );

    }, 250);

}


/* =========================================
   KPI CARDS
========================================= */

function renderKPIs(result) {

    const grid =
        document.getElementById(
            "kpiGrid"
        );


    const sources =
        Array.isArray(result.sources)
            ? result.sources.length
            : 0;


    const related =
        Array.isArray(
            result.related_entities
        )
            ? result.related_entities.length
            : 0;


    const risks =
        Array.isArray(
            result.risk_factors
        )
            ? result.risk_factors.length
            : 0;


    const news =
        result.negative_news
            ? "YES"
            : "NO";


    const cards = [

        {
            label: "Sources",
            value: sources,
            icon: "◉"
        },

        {
            label: "Related Entities",
            value: related,
            icon: "◎"
        },

        {
            label: "Risk Factors",
            value: risks,
            icon: "⚠"
        },

        {
            label: "Adverse Media",
            value: news,
            icon: "◈"
        }

    ];


    grid.innerHTML =
        cards.map(
            (card, index) => `

            <div
                class="
                    glass
                    rounded-2xl
                    p-5
                    result-card
                "
                style="
                    animation-delay:
                    ${index * 80}ms
                "
            >

                <div class="
                    flex
                    items-center
                    justify-between
                ">

                    <span class="
                        text-xs
                        uppercase
                        tracking-widest
                        text-gray-500
                    ">
                        ${card.label}
                    </span>

                    <span class="text-cyan-400">
                        ${card.icon}
                    </span>

                </div>


                <div class="
                    text-3xl
                    font-black
                    mt-4
                ">
                    ${escapeHtml(
                        card.value
                    )}
                </div>

            </div>

        `
        ).join("");
}


/* =========================================
   ENTITY CARD
========================================= */

function renderEntity(result) {

    const card =
        document.getElementById(
            "entityCard"
        );


    const rows = [

        [
            "Industry",
            result.industry ||
            "Not identified"
        ],

        [
            "Jurisdiction",
            result.jurisdiction ||
            "Not identified"
        ],

        [
            "Entity Type",
            result.entity_type ||
            "Unknown"
        ]

    ];


    card.innerHTML = `

        <div class="
            text-xs
            uppercase
            tracking-[.25em]
            text-cyan-400
        ">
            Entity Intelligence
        </div>


        <h3 class="
            text-2xl
            font-bold
            mt-2
        ">
            Profile
        </h3>


        <div class="mt-6">

            ${rows.map(
                row => `

                <div class="data-row">

                    <span class="text-gray-500">
                        ${row[0]}
                    </span>


                    <span class="
                        text-gray-200
                        text-right
                        max-w-[60%]
                    ">
                        ${escapeHtml(
                            row[1]
                        )}
                    </span>

                </div>

            `
            ).join("")}

        </div>


        ${
            result.addresses?.length
                ? `

            <div class="mt-6">

                <div class="
                    text-xs
                    uppercase
                    tracking-widest
                    text-gray-600
                    mb-3
                ">
                    Known Addresses
                </div>


                <div class="space-y-2">

                    ${
                        result.addresses.map(
                            address => `

                        <div class="
                            rounded-xl
                            bg-white/[.03]
                            border
                            border-white/5
                            px-4
                            py-3
                            text-sm
                            text-gray-400
                        ">
                            ${escapeHtml(
                                address
                            )}
                        </div>

                    `
                        ).join("")
                    }

                </div>

            </div>

            `
                : ""
        }

    `;
}


/* =========================================
   ADDRESS CARD
========================================= */

function renderAddress(result) {

    const card =
        document.getElementById(
            "addressCard"
        );


    const addresses =
        result.addresses || [];


    const entities =
        result.related_entities || [];


    card.innerHTML = `

        <div class="
            text-xs
            uppercase
            tracking-[.25em]
            text-blue-400
        ">
            Location Intelligence
        </div>


        <h3 class="
            text-2xl
            font-bold
            mt-2
        ">
            Address & Associations
        </h3>


        <div class="mt-6">

            <div class="
                text-xs
                uppercase
                tracking-widest
                text-gray-600
                mb-3
            ">
                Addresses
            </div>


            ${
                addresses.length
                    ? addresses.map(
                        address => `

                    <div class="
                        rounded-xl
                        bg-white/[.03]
                        border
                        border-white/5
                        px-4
                        py-3
                        mb-2
                        text-sm
                        text-gray-300
                    ">
                        ${escapeHtml(
                            address
                        )}
                    </div>

                `
                    ).join("")
                    : `
                    <div class="
                        text-gray-600
                        text-sm
                    ">
                        No additional addresses identified.
                    </div>
                `
            }

        </div>


        <div class="mt-7">

            <div class="
                text-xs
                uppercase
                tracking-widest
                text-gray-600
                mb-3
            ">
                Associated Entities
            </div>


            ${
                entities.length
                    ? `

                <div class="
                    flex
                    flex-wrap
                    gap-2
                ">

                    ${
                        entities.map(
                            entity => `

                            <span class="
                                px-3
                                py-2
                                rounded-xl
                                bg-blue-400/5
                                border
                                border-blue-400/10
                                text-sm
                                text-blue-300
                            ">
                                ${escapeHtml(
                                    entity
                                )}
                            </span>

                        `
                        ).join("")
                    }

                </div>

                `
                    : `

                <div class="
                    text-gray-600
                    text-sm
                ">
                    No associated entities identified.
                </div>

                `
            }

        </div>

    `;
}


/* =========================================
   NEGATIVE NEWS
========================================= */

function renderNews(result) {

    const card =
        document.getElementById(
            "newsCard"
        );


    const negative =
        Boolean(
            result.negative_news
        );


    card.innerHTML = `

        <div class="
            flex
            flex-col
            md:flex-row
            md:items-center
            justify-between
            gap-4
        ">

            <div>

                <div class="
                    text-xs
                    uppercase
                    tracking-[.25em]
                    ${
                        negative
                            ? "text-red-400"
                            : "text-emerald-400"
                    }
                ">
                    Adverse Media Intelligence
                </div>


                <h3 class="
                    text-2xl
                    font-bold
                    mt-2
                ">
                    Negative News Analysis
                </h3>

            </div>


            <div class="
                px-4
                py-2
                rounded-full
                ${
                    negative
                        ? "bg-red-400/10 text-red-300 border-red-400/20"
                        : "bg-emerald-400/10 text-emerald-300 border-emerald-400/20"
                }
                border
                text-sm
                font-bold
            ">

                ${
                    negative
                        ? "⚠ ADVERSE INFORMATION FOUND"
                        : "✓ NO QUALIFYING ADVERSE MEDIA"
                }

            </div>

        </div>


        <div class="
            mt-6
            rounded-2xl
            bg-black/20
            border
            border-white/5
            p-5
            text-gray-400
            leading-7
        ">

            ${
                escapeHtml(
                    result.negative_news_summary ||
                    "No adverse-media summary was generated."
                )
            }

        </div>

    `;
}


/* =========================================
   RISK FACTORS
========================================= */

function renderRiskFactors(result) {

    const card =
        document.getElementById(
            "riskFactorsCard"
        );


    const factors =
        result.risk_factors || [];


    const sanctions =
        result.sanctions || {};


    card.innerHTML = `

        <div class="
            text-xs
            uppercase
            tracking-[.25em]
            text-orange-400
        ">
            Risk Intelligence
        </div>


        <h3 class="
            text-2xl
            font-bold
            mt-2
        ">
            Risk Factors & Sanctions
        </h3>


        <div class="mt-6">

            ${
                factors.length
                    ? factors.map(
                        (factor, index) => {

                            const severity =
                                String(
                                    factor.severity ||
                                    "Low"
                                ).toLowerCase();


                            const severityClass =
                                severity === "critical"
                                    ? "text-red-400 bg-red-400/10"
                                    :
                                severity === "high"
                                    ? "text-orange-400 bg-orange-400/10"
                                    :
                                severity === "medium"
                                    ? "text-yellow-400 bg-yellow-400/10"
                                    :
                                    "text-emerald-400 bg-emerald-400/10";


                            return `

                                <div class="
                                    rounded-2xl
                                    border
                                    border-white/5
                                    bg-white/[.02]
                                    p-5
                                    mb-3
                                    result-card
                                "
                                style="
                                    animation-delay:
                                    ${index * 100}ms
                                ">

                                    <div class="
                                        flex
                                        items-start
                                        justify-between
                                        gap-4
                                    ">

                                        <div>

                                            <div class="
                                                font-semibold
                                                text-white
                                            ">
                                                ${escapeHtml(
                                                    factor.category
                                                )}
                                            </div>


                                            <p class="
                                                text-sm
                                                text-gray-500
                                                mt-2
                                                leading-6
                                            ">
                                                ${escapeHtml(
                                                    factor.description
                                                )}
                                            </p>

                                        </div>


                                        <span class="
                                            shrink-0
                                            px-3
                                            py-1
                                            rounded-full
                                            text-xs
                                            font-bold
                                            ${severityClass}
                                        ">
                                            ${escapeHtml(
                                                factor.severity
                                            )}
                                        </span>

                                    </div>

                                </div>

                            `;

                        }
                    ).join("")
                    : `

                    <div class="
                        rounded-2xl
                        bg-emerald-400/5
                        border
                        border-emerald-400/10
                        p-5
                        text-emerald-300
                    ">
                        ✓ No risk factors identified.
                    </div>

                `
            }

        </div>


        <div class="
            mt-6
            ${
                sanctions.listed
                    ? "bg-red-400/5 border-red-400/20"
                    : "bg-emerald-400/5 border-emerald-400/10"
            }
            border
            rounded-2xl
            p-5
        ">

            <div class="font-bold">

                ${
                    sanctions.listed
                        ? "⚠ Sanctions Match"
                        : "✓ No Sanctions Match Identified"
                }

            </div>


            ${
                sanctions.details
                    ? `

                    <p class="
                        text-sm
                        text-gray-500
                        mt-2
                    ">
                        ${escapeHtml(
                            sanctions.details
                        )}
                    </p>

                    `
                    : ""
            }

        </div>

    `;
}


/* =========================================
   SOURCES
========================================= */

function renderSources(result) {

    const card =
        document.getElementById(
            "sourcesCard"
        );


    const sources =
        result.sources || [];


    card.innerHTML = `

        <div class="
            flex
            items-center
            justify-between
        ">

            <div>

                <div class="
                    text-xs
                    uppercase
                    tracking-[.25em]
                    text-gray-500
                ">
                    Evidence
                </div>


                <h3 class="
                    text-2xl
                    font-bold
                    mt-2
                ">
                    Source Intelligence
                </h3>

            </div>


            <div class="
                text-sm
                text-gray-500
            ">
                ${sources.length} sources
            </div>

        </div>


        <div class="
            grid
            md:grid-cols-2
            gap-3
            mt-6
        ">

            ${
                sources.length
                    ? sources.map(
                        (url, index) => `

                        <a
                            href="${escapeHtml(url)}"
                            target="_blank"
                            rel="noopener noreferrer"
                            class="
                                source-link
                                rounded-2xl
                                border
                                border-white/5
                                bg-white/[.02]
                                p-4
                                flex
                                gap-4
                                items-start
                            "
                        >

                            <div class="
                                w-8
                                h-8
                                rounded-lg
                                bg-cyan-400/10
                                text-cyan-300
                                flex
                                items-center
                                justify-center
                                text-xs
                                font-bold
                                shrink-0
                            ">
                                ${index + 1}
                            </div>


                            <div class="
                                text-sm
                                text-gray-400
                                break-all
                            ">
                                ${escapeHtml(url)}
                            </div>

                        </a>

                    `
                    ).join("")
                    : `

                    <div class="
                        text-gray-600
                        text-sm
                    ">
                        No sources available.
                    </div>

                `
            }

        </div>

    `;
}


/* =========================================
   LIMITATIONS
========================================= */

function renderLimitations(result) {

    const container =
        document.getElementById(
            "limitations"
        );


    const limitations =
        result.limitations || [];


    if (!limitations.length) {

        container.innerHTML = "";

        return;
    }


    container.innerHTML = `

        <div class="
            text-xs
            uppercase
            tracking-widest
            text-gray-600
            mb-3
        ">
            Investigation Limitations
        </div>


        <div class="space-y-2">

            ${
                limitations.map(
                    item => `

                    <div class="
                        text-sm
                        text-gray-500
                        flex
                        gap-2
                    ">

                        <span class="text-yellow-500">
                            •
                        </span>


                        <span>
                            ${escapeHtml(item)}
                        </span>

                    </div>

                `
                ).join("")
            }

        </div>

    `;
}


/* =========================================
   RENDER EVERYTHING
========================================= */

function renderResults(result) {

    document.getElementById(
        "resultEntity"
    ).textContent =
        result.entity ||
        "Unknown Entity";


    document.getElementById(
        "resultDescription"
    ).textContent =
        result.description ||
        "";


    document.getElementById(
        "entityType"
    ).textContent =
        result.entity_type ||
        "Unknown";


    document.getElementById(
        "assessmentSummary"
    ).textContent =
        result.assessment_summary ||
        "";


    renderRisk(result);

    renderKPIs(result);

    renderEntity(result);

    renderAddress(result);

    renderNews(result);

    renderRiskFactors(result);

    renderSources(result);

    renderLimitations(result);


    results.classList.remove(
        "hidden"
    );


    results.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}


/* =========================================
   FORM
========================================= */

form.addEventListener(
    "submit",
    async event => {

        event.preventDefault();


        const entityName =
            document.getElementById(
                "entityName"
            ).value.trim();


        const address =
            document.getElementById(
                "targetAddress"
            ).value.trim();


        if (!entityName) {

            showError(
                "Target name is required."
            );

            return;
        }


        showLoading();


        try {

            const response =
                await fetch(
                    "/api/analyze",
                    {

                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({

                            entity_name:
                                entityName,

                            address:
                                address

                        })

                    }
                );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    "The analysis request failed."
                );

            }


            await sleep(400);


            hideLoading();


            renderResults(data);

        }


        catch (error) {

            hideLoading();


            showError(
                error.message ||
                "Unable to complete analysis."
            );

        }

    }
);