from flask import Flask, render_template, request, jsonify
import logging
import plotly.graph_objects as go
import numpy as np
import math

# Configure logging with debug level enabled
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Solvent database (HSP values)
SOLVENTS = {
    "Water": {"d": 15.5, "p": 16.0, "h": 42.3},
    "Ethanol": {"d": 15.8, "p": 8.8, "h": 19.4},
    "Acetone": {"d": 15.5, "p": 10.4, "h": 7.0},
    "Toluene": {"d": 18.0, "p": 1.4, "h": 2.0},
    "Hexane": {"d": 14.9, "p": 0.0, "h": 0.0},
    "MTBE": {"d": 15.3, "p": 4.0, "h": 2.6},
    "Ethyl acetate": {"d": 15.8, "p": 5.3, "h": 7.2},
    "MIBK": {"d": 15.3, "p": 4.1, "h": 5.1},
    "Heptane": {"d": 15.3, "p": 0.0, "h": 0.0},
    "Rapeseed oil": {"d": 17.0, "p": 2.0, "h": 5.0},
    "Dimethyl sulfoxide (DMSO)": {"d": 18.4, "p": 16.4, "h": 10.2},
    "Propylene carbonate": {"d": 20.0, "p": 18.0, "h": 4.1},
    "N-Methyl-2-pyrrolidone (NMP)": {"d": 18.0, "p": 12.3, "h": 7.2},
    "γ-Butyrolactone (GBL)": {"d": 19.0, "p": 16.6, "h": 7.4},
    "Chloroform": {"d": 17.8, "p": 3.1, "h": 5.7},
    "Acetonitrile": {"d": 15.3, "p": 18.0, "h": 6.1},
    "Dichloromethane (DCM)": {"d": 18.2, "p": 6.3, "h": 7.1},
    "Anisole": {"d": 19.2, "p": 1.0, "h": 4.1},
    "Cyclohexanone": {"d": 17.8, "p": 5.1, "h": 8.4},
    "Tetrahydrofuran (THF)": {"d": 16.8, "p": 5.7, "h": 8.0}
}

# Solute presets
SOLUTES = {
    "Piceatannol": {"d": 20.1, "p": 8.5, "h": 12.3, "ro": 5.0},
    "Resveratrol": {"d": 19.4, "p": 7.8, "h": 10.9, "ro": 5.2},
    "Curcumin": {"d": 18.2, "p": 8.6, "h": 11.5, "ro": 5.5},
    "Quercetin": {"d": 21.3, "p": 9.4, "h": 14.2, "ro": 4.8},
    "Genistein": {"d": 19.0, "p": 8.0, "h": 11.8, "ro": 5.1},
    "Luteolin": {"d": 20.0, "p": 9.2, "h": 12.7, "ro": 5.0},
    "Pterostilbene": {"d": 19.2, "p": 6.9, "h": 9.8, "ro": 5.3},
    "Apigenin": {"d": 19.6, "p": 7.2, "h": 12.1, "ro": 5.2},  # Found in chamomile, parsley
    "Baicalein": {"d": 18.7, "p": 8.0, "h": 10.5, "ro": 5.3},  # Found in skullcap
    "Catechin": {"d": 21.0, "p": 9.1, "h": 14.5, "ro": 5.0},  # Found in tea, cocoa
    "Epicatechin": {"d": 20.8, "p": 8.9, "h": 13.9, "ro": 5.0},  # Found in green tea, cocoa
    "Hesperetin": {"d": 19.2, "p": 7.6, "h": 10.7, "ro": 5.1},  # Found in citrus fruits
    "Kaempferol": {"d": 20.2, "p": 9.0, "h": 13.2, "ro": 5.0},  # Found in broccoli, kale
    "Myricetin": {"d": 21.4, "p": 9.7, "h": 15.0, "ro": 4.9},  # Found in berries, tea
    "Naringenin": {"d": 19.0, "p": 7.5, "h": 11.0, "ro": 5.2},  # Found in citrus fruits
    "Rutin": {"d": 21.6, "p": 9.8, "h": 16.3, "ro": 4.8},  # Found in buckwheat, citrus fruits
    "Taxifolin": {"d": 20.7, "p": 8.8, "h": 13.7, "ro": 5.0}  # Found in milk thistle, onions
}


def calculate_distance(solute, solvent):
    try:
        distance = math.sqrt(
            4 * (solute["d"] - solvent["d"]) ** 2 +
            (solute["p"] - solvent["p"]) ** 2 +
            (solute["h"] - solvent["h"]) ** 2
        )
        logger.debug("Calculated distance (Ra): %s for solute %s and solvent %s", distance, solute, solvent)
        return distance
    except KeyError as e:
        raise ValueError(f"Missing HSP parameter: {e}")


def create_3d_plot(plot_data, solute=None):
    logger.debug("Creating 3D plot with plot_data: %s and solute: %s", plot_data, solute)
    fig = go.Figure()

    # Add solvent points
    fig.add_trace(go.Scatter3d(
        x=plot_data["d_values"],
        y=plot_data["p_values"],
        z=plot_data["h_values"],
        mode="markers+text",
        marker=dict(
            size=10,
            color=plot_data["colors"],
            opacity=0.8,
            symbol="circle"
        ),
        text=plot_data["solvents"],
        hoverinfo="text",
        hovertext=[f"{name}: (δD={d:.1f}, δP={p:.1f}, δH={h:.1f})"
                   for name, d, p, h in zip(
                plot_data["solvents"],
                plot_data["d_values"],
                plot_data["p_values"],
                plot_data["h_values"]
            )],
        name="Solvents"
    ))

    # Add solute point and sphere (if provided)
    if solute:
        fig.add_trace(go.Scatter3d(
            x=[solute["d"]],
            y=[solute["p"]],
            z=[solute["h"]],
            mode="markers+text",
            marker=dict(
                size=14,
                color="blue",
                opacity=0.9,
                symbol="diamond"
            ),
            text=["Solute"],
            hoverinfo="text",
            hovertext=f"Solute: (δD={solute['d']:.1f}, δP={solute['p']:.1f}, δH={solute['h']:.1f})",
            name="Solute"
        ))

        if "ro" in solute:
            u, v = np.mgrid[0:2 * np.pi:20j, 0:np.pi:10j]
            radius = solute["ro"]
            x = radius * np.cos(u) * np.sin(v) + solute["d"]
            y = radius * np.sin(u) * np.sin(v) + solute["p"]
            z = radius * np.cos(v) + solute["h"]

            fig.add_trace(go.Surface(
                x=x, y=y, z=z,
                opacity=0.2,
                colorscale=[[0, 'blue'], [1, 'blue']],
                showscale=False,
                name="Solubility Sphere"
            ))

    fig.update_layout(
        scene=dict(
            xaxis_title="δD (Dispersion)",
            yaxis_title="δP (Polar)",
            zaxis_title="δH (Hydrogen Bonding)",
            aspectmode='cube',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.2)
            )
        ),
        title="Hansen Solubility Parameters in 3D Space",
        margin=dict(l=0, r=0, b=0, t=30),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        height=600
    )
    fig_json = fig.to_json()
    logger.debug("Generated plot JSON: %s", fig_json)
    return fig_json


def get_solute_from_request(data):
    solute_name = data.get("solute_name")
    if solute_name and solute_name in SOLUTES:
        logger.debug("Using preset solute: %s", solute_name)
        return SOLUTES[solute_name]
    else:
        try:
            solute = {
                "d": float(data["solute_d"]),
                "p": float(data["solute_p"]),
                "h": float(data["solute_h"]),
                "ro": float(data["solute_ro"])
            }
            logger.debug("Using custom solute parameters: %s", solute)
            return solute
        except (KeyError, ValueError) as e:
            raise ValueError(f"Invalid solute parameters: {str(e)}")


def get_solubility_status(red_value):
    # Adjusted thresholds: values equal to 1 are now considered "Soluble"
    if red_value <= 1:
        return "Soluble", "green"
    elif red_value <= 1.5:
        return "Partially Soluble", "orange"
    else:
        return "Insoluble", "red"


@app.route("/")
def index():
    logger.debug("Rendering index page")
    return render_template("index.html", solvents=sorted(SOLVENTS.keys()), solutes=SOLUTES)


@app.route("/api/search_solvents", methods=["GET"])
def search_solvents():
    query = request.args.get("q", "").lower()
    logger.debug("Search solvents query: '%s'", query)
    results = [{"name": name} for name in SOLVENTS if query in name.lower()]
    logger.debug("Search solvents results: %s", results)
    return jsonify(results)


@app.route("/api/calculate", methods=["POST"])
def calculate():
    try:
        data = request.get_json()
        logger.debug("Received calculation request: %s", data)
        if not data:
            return jsonify({"error": "No data provided"}), 400

        try:
            solute = get_solute_from_request(data)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        if solute["ro"] <= 0:
            return jsonify({"error": "Ro must be positive"}), 400

        selected_solvents = data.get("solvents", [])
        if not selected_solvents:
            return jsonify({"error": "No solvents selected"}), 400

        results = {}
        plot_data = {"solvents": [], "d_values": [], "p_values": [], "h_values": [], "colors": []}

        for solvent_name in selected_solvents:
            solvent = SOLVENTS.get(solvent_name)
            if not solvent:
                logger.warning("Solvent %s not found", solvent_name)
                continue

            ra = calculate_distance(solute, solvent)
            red = ra / solute["ro"]
            solubility, color = get_solubility_status(red)

            results[solvent_name] = {
                "d": solvent["d"],
                "p": solvent["p"],
                "h": solvent["h"],
                "ra": round(ra, 2),
                "red": round(red, 2),
                "solubility": solubility
            }

            plot_data["solvents"].append(solvent_name)
            plot_data["d_values"].append(solvent["d"])
            plot_data["p_values"].append(solvent["p"])
            plot_data["h_values"].append(solvent["h"])
            plot_data["colors"].append(color)

        plot_json = create_3d_plot(plot_data, solute)
        logger.debug("Calculation results: %s", results)

        return jsonify({"results": results, "plot_json": plot_json})

    except Exception as e:
        logger.error("Error in calculate: %s", str(e))
        return jsonify({"error": f"Calculation failed: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
