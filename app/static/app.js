async function api(url, options = {}) {

    const response = await fetch(
        url,
        {
            credentials: "include",
            ...options
        }
    );

    let data = {};

    try {
        data = await response.json();
    }
    catch {}

    if (!response.ok) {

        throw new Error(
            data.detail ||
            "Request failed"
        );
    }

    return data;
}


function escapeHTML(value) {

    return String(value).replace(
        /[&<>"']/g,
        function (char) {

            return {
                "&": "&amp;",
                "<": "&lt;",
                ">": "&gt;",
                '"': "&quot;",
                "'": "&#039;"
            }[char];

        }
    );
}


function logout() {

    api(
        "/logout",
        {
            method: "POST"
        }
    )
    .finally(
        () => {
            window.location = "/";
        }
    );
}


function loginForm() {

    const form =
        document.querySelector(
            "#loginForm"
        );

    form.onsubmit =
        async function (event) {

            event.preventDefault();

            try {

                await api(
                    "/login",
                    {
                        method: "POST",

                        body:
                            new URLSearchParams(
                                new FormData(
                                    form
                                )
                            )
                    }
                );

                window.location =
                    "/dashboard";

            }
            catch (error) {

                document.querySelector(
                    "#msg"
                ).textContent =
                    error.message;
            }
        };
}


function registerForm() {

    const form =
        document.querySelector(
            "#registerForm"
        );

    form.onsubmit =
        async function (event) {

            event.preventDefault();

            try {

                const payload =
                    Object.fromEntries(
                        new FormData(form)
                    );

                await api(
                    "/register",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify(
                                payload
                            )
                    }
                );

                window.location =
                    "/login";

            }
            catch (error) {

                document.querySelector(
                    "#msg"
                ).textContent =
                    error.message;
            }
        };
}


function parseItems(value) {

    const result = {};

    value
        .split(",")
        .forEach(
            function (item) {

                const parts =
                    item.split("=");

                if (parts[0]) {

                    result[
                        parts[0].trim()
                    ] =
                        Number(
                            parts[1] || 1
                        );
                }
            }
        );

    return result;
}


function money(number) {

    return "₹" +
        Number(number)
            .toLocaleString(
                "en-IN",
                {
                    maximumFractionDigits: 0
                }
            );
}


function renderResult(data) {

    const result =
        data.result;

    return `

<section class="card result">

<span class="badge">
${escapeHTML(result.source_mode)}
</span>

<h2>
${escapeHTML(result.title)}
</h2>

<p>
${escapeHTML(result.summary)}
</p>

<div class="metrics">

<div class="metric">

Used

<b>
${money(result.budget_used)}
</b>

</div>

<div class="metric">

Remaining

<b>
${money(result.budget_remaining)}
</b>

</div>

<div class="metric">

Plan ID

<b>
#${data.id}
</b>

</div>

</div>


<h3>
Budget Allocation
</h3>

<div class="items">

${result.allocations.map(

    function (item) {

        return `

<div class="metric">

${escapeHTML(
    item.category
)}

<b>
${money(item.amount)}
</b>

${item.percentage}%

</div>

`;

    }

).join("")}

</div>


<h3>
Recommendations
</h3>


<div class="items">

${result.recommendations.map(

    function (item) {

        return `

<article class="item">

<span class="badge">

${escapeHTML(
    item.platform
)}

</span>

<h3>

${escapeHTML(
    item.name
)}

</h3>

<b>

${money(
    item.estimated_price
)}

</b>

<p>

${escapeHTML(
    item.reason
)}

</p>

<a
    target="_blank"
    rel="noopener"
    href="${item.search_url}"
>
Search platform →
</a>

</article>

`;

    }

).join("")}

</div>


<h3>
Tips
</h3>

<ul>

${result.tips.map(

    function (tip) {

        return `
<li>
${escapeHTML(tip)}
</li>
`;

    }

).join("")}

</ul>

</section>

`;
}


async function protect() {

    try {

        return await api(
            "/session-info"
        );

    }
    catch {

        window.location =
            "/login";
    }
}


function homePlanner() {

    const form =
        document.querySelector(
            "#homeForm"
        );

    form.onsubmit =
        async function (event) {

            event.preventDefault();

            const data =
                new FormData(form);

            try {

                await protect();

                const payload = {

                    budget:
                        Number(
                            data.get(
                                "budget"
                            )
                        ),

                    rooms:
                        data
                            .get("rooms")
                            .split(",")
                            .map(
                                x =>
                                    x.trim()
                            ),

                    style:
                        data.get(
                            "style"
                        ),

                    items:
                        parseItems(
                            data.get(
                                "items"
                            )
                        ),

                    priorities:
                        data.get(
                            "priorities"
                        )
                };

                const result =
                    await api(
                        "/generate-home",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body:
                                JSON.stringify(
                                    payload
                                )
                        }
                    );

                document.querySelector(
                    "#results"
                ).innerHTML =
                    renderResult(
                        result
                    );

            }
            catch (error) {

                document.querySelector(
                    "#msg"
                ).textContent =
                    error.message;
            }
        };
}


function partyPlanner() {

    const form =
        document.querySelector(
            "#partyForm"
        );

    form.onsubmit =
        async function (event) {

            event.preventDefault();

            const data =
                new FormData(form);

            try {

                await protect();

                const payload = {

                    budget:
                        Number(
                            data.get(
                                "budget"
                            )
                        ),

                    guests:
                        Number(
                            data.get(
                                "guests"
                            )
                        ),

                    event_type:
                        data.get(
                            "event_type"
                        ),

                    venue:
                        data.get(
                            "venue"
                        ),

                    city:
                        data.get(
                            "city"
                        ),

                    preferences:
                        data.get(
                            "preferences"
                        )
                };

                const result =
                    await api(
                        "/generate-party",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body:
                                JSON.stringify(
                                    payload
                                )
                        }
                    );

                document.querySelector(
                    "#results"
                ).innerHTML =
                    renderResult(
                        result
                    );

            }
            catch (error) {

                document.querySelector(
                    "#msg"
                ).textContent =
                    error.message;
            }
        };
}


function jewelryPlanner() {

    const form =
        document.querySelector(
            "#jewelryForm"
        );

    form.onsubmit =
        async function (event) {

            event.preventDefault();

            try {

                await protect();

                const result =
                    await api(
                        "/generate-jewelry",
                        {
                            method: "POST",

                            body:
                                new FormData(
                                    form
                                )
                        }
                    );

                document.querySelector(
                    "#results"
                ).innerHTML =
                    renderResult(
                        result
                    );

            }
            catch (error) {

                document.querySelector(
                    "#msg"
                ).textContent =
                    error.message;
            }
        };
}


async function dashboard() {

    try {

        const data =
            await api(
                "/session-data"
            );

        document.querySelector(
            "#dashboard"
        ).innerHTML = `

<div class="cards">

<div class="card">

<h2>
${escapeHTML(
    data.user.full_name
)}
</h2>

<p>
${escapeHTML(
    data.user.email
)}
</p>

</div>


<div class="card">

<h2>
${data.recommendation_count}
</h2>

<p>
Saved recommendations
</p>

</div>


<div class="card">

<h2>
3
</h2>

<p>
Planner modules
</p>

</div>

</div>

`;

    }
    catch {

        window.location =
            "/login";
    }
}


async function historyPage() {

    try {

        const rows =
            await api(
                "/history"
            );

        if (!rows.length) {

            document.querySelector(
                "#history"
            ).innerHTML =
                "<p>No recommendations yet.</p>";

            return;
        }

        document.querySelector(
            "#history"
        ).innerHTML =

            rows.map(

                function (row) {

                    return `

<div class="row">

<div>

<b>
${escapeHTML(
    row.title
)}
</b>

<br>

${escapeHTML(
    row.planner_type
)}

·

${money(
    row.budget
)}

·

${new Date(
    row.created_at
).toLocaleString()}

</div>

<button
    class="btn"
    onclick="details(${row.id})"
>
Open
</button>

</div>

`;

                }

            ).join("");

    }
    catch {

        window.location =
            "/login";
    }
}


async function details(id) {

    try {

        const data =
            await api(
                "/recommendations-details/"
                + id
            );

        document.querySelector(
            "#history"
        ).insertAdjacentHTML(
            "afterbegin",
            renderResult(data)
        );

    }
    catch (error) {

        alert(
            error.message
        );
    }
}