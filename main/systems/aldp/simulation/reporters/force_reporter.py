# Source: https://github.com/davidjtoomer/openmm-numpy-reporters

# Adaptation of the ForceReporter class from
# http://docs.openmm.org/latest/userguide/application/04_advanced_sim_examples.html#extracting-and-reporting-forces-and-other-data
# using appendable Numpy files.

from openmm import State
from openmm.app import Simulation
from openmm.unit import *
from reporters.numpy_append import NumpyAppendFile
import numpy as np

class ForceReporter:
    def __init__(self, filename: str, report_interval: int, buffer_size: int = None, sel_indices=None):
        """
        Initialize a ForceReporter object.

        Parameters
        ----------
        filename : str
            The filename of the file to write to.
        report_interval : int
            The interval (in time steps) at which to write frames.
        buffer_size (optional): int
            The number of frames to buffer before writing to disk. Default: None.
        sel_indices (optional): list
            The indices of the atoms to write forces for. Default: None.
        """

        self.filename = filename
        self.report_interval = report_interval
        self.sel_indices = sel_indices

        self.buffer_size = buffer_size
        self.buffer = None
        self.current_buffer_pos = 0

    def report(self, simulation: Simulation, state: State):
        """
        Generate a report.

        Parameters
        ----------
        simulation : Simulation
            The simulation to generate a report for.
        state : State
            The current state of the simulation.
        """

        forces = state.getForces(asNumpy=True).value_in_unit(
            kilocalories_per_mole / angstrom
        )[None, ...]

        if self.sel_indices is not None:
            forces = forces[:, self.sel_indices, :]

        if self.buffer_size is not None: # use buffer instead of always writing to disk

            if self.buffer is None:
                self.buffer = np.empty(shape=(self.buffer_size, *forces.shape[1:]))

            self.buffer[self.current_buffer_pos:self.current_buffer_pos + 1,...] = forces
            self.current_buffer_pos += 1

            if self.current_buffer_pos == self.buffer_size:
                with NumpyAppendFile(self.filename) as file:
                    file.append(self.buffer)
                self.buffer = None
                self.current_buffer_pos = 0

        else:

            with NumpyAppendFile(self.filename) as file:
                file.append(forces)

    def describeNextReport(self, simulation: Simulation):
        """
        Get information about the next report that will be generated.

        Parameters
        ----------
        simulation : Simulation
            The simulation to generate a report for.
        """
        steps = self.report_interval - simulation.currentStep % self.report_interval
        return (steps, False, False, True, False, None)

    def __del__(self):
        """
        Write any remaining frames in buffer to disk.
        """

        if self.buffer is not None:
            with NumpyAppendFile(self.filename) as file:
                file.append(self.buffer[:self.current_buffer_pos,...])