#####################################################################################################
# “PrOMMiS” was produced under the DOE Process Optimization and Modeling for Minerals Sustainability
# (“PrOMMiS”) initiative, and is copyright (c) 2023-2025 by the software owners: The Regents of the
# University of California, through Lawrence Berkeley National Laboratory, et al. All rights reserved.
# Please see the files COPYRIGHT.md and LICENSE.md for full copyright and license information.
#####################################################################################################

from pyomo.environ import check_optimal_termination, value

from idaes.core.initialization import InitializationStatus
from idaes.core.solvers import get_solver
from idaes.core.util import DiagnosticsToolbox

import pytest

from prommis.solvent_extraction.mixer_settler_extraction import (
    MixerSettlerExtractionInitializer,
)
from prommis.solvent_extraction.mixer_settler_ex_flowsheet_steady import (
    model_buildup_and_set_inputs,
    main,
)


solver = get_solver()


class Test_Mixer_Settler_EX_steady_model:
    @pytest.fixture(scope="class")
    def Mix_Settle_Ex_frame(self):
        dosage = 5
        number_of_stages = 3
        m = model_buildup_and_set_inputs(dosage, number_of_stages)

        return m

    @pytest.mark.component
    def test_structural_issues(self, Mix_Settle_Ex_frame):
        model = Mix_Settle_Ex_frame
        dt = DiagnosticsToolbox(model)
        dt.assert_no_structural_warnings()

    @pytest.mark.component
    def test_initialization(self, Mix_Settle_Ex_frame):
        model = Mix_Settle_Ex_frame
        initializer = model.fs.mixer_settler_ex.default_initializer()
        assert (
            model.fs.mixer_settler_ex.default_initializer
            is MixerSettlerExtractionInitializer
        )
        initializer.initialize(model.fs.mixer_settler_ex)

        assert (
            initializer.summary[model.fs.mixer_settler_ex]["status"]
            == InitializationStatus.Ok
        )

    @pytest.mark.solver
    @pytest.mark.skipif(solver is None, reason="Solver not available")
    @pytest.mark.component
    def test_solve(self, Mix_Settle_Ex_frame):
        m = Mix_Settle_Ex_frame
        results = solver.solve(m, tee=True)

        # Check for optimal solution
        assert check_optimal_termination(results)

    @pytest.mark.component
    @pytest.mark.solver
    def test_numerical_issues(self, Mix_Settle_Ex_frame):
        model = Mix_Settle_Ex_frame
        dt = DiagnosticsToolbox(model)
        dt.assert_no_numerical_warnings()

    @pytest.mark.component
    @pytest.mark.solver
    def test_solution(self, Mix_Settle_Ex_frame):

        model = Mix_Settle_Ex_frame
        aqueous_outlet = {
            "H2O": 1000000,
            "H": 39.5131,
            "SO4": 2056.395,
            "HSO4": 8023.225,
            "Al": 399.95,
            "Ca": 102.336,
            "Cl": 9.9999e-8,
            "Ce": 2.1056,
            "Dy": 0.0010159,
            "Fe": 585.5947,
            "Gd": 0.19119,
            "La": 0.91421,
            "Nd": 0.8801,
            "Pr": 0.27631,
            "Sc": 0.0027415,
            "Sm": 0.08669,
            "Y": 4.27516e-06,
        }

        organic_outlet = {
            "Al_o": 22.4249,
            "Ca_o": 7.2059,
            "Ce_o": 0.17168,
            "DEHPA": 46086.719,
            "Dy_o": 0.045992,
            "Fe_o": 102.6712,
            "Gd_o": 0.06723,
            "Kerosene": 820000,
            "La_o": 0.07189,
            "Nd_o": 0.06606,
            "Pr_o": 0.026727,
            "Sc_o": 1.7632,
            "Sm_o": 0.010323,
            "Y_o": 0.12401,
        }

        for k, v in model.fs.mixer_settler_ex.organic_outlet.conc_mass_comp.items():
            assert value(v) == pytest.approx(organic_outlet[k[1]], rel=1e-4)

        for k, v in model.fs.mixer_settler_ex.aqueous_outlet.conc_mass_comp.items():
            assert value(v) == pytest.approx(aqueous_outlet[k[1]], rel=1e-4)

    @pytest.fixture(scope="class")
    def Mix_Settle_Ex_total_flowsheet(self):
        dosage = 5
        number_of_stages = 3
        model, results = main(dosage, number_of_stages)

        return model, results

    @pytest.mark.component
    def test_solve_total(self, Mix_Settle_Ex_total_flowsheet):
        m, results = Mix_Settle_Ex_total_flowsheet
        assert check_optimal_termination(results)
