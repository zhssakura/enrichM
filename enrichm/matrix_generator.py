#!/usr/bin/env python2
###############################################################################
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program. If not, see <http://www.gnu.org/licenses/>.        #
#                                                                             #
###############################################################################
 
__author__ = "Joel Boyd"
__copyright__ = "Copyright 2017"
__credits__ = ["Joel Boyd"]
__license__ = "GPL3"
__version__ = "0.0.1"
__maintainer__ = "Joel Boyd"
__email__ = "joel.boyd near uq.net.au"
__status__ = "Development"
 
###############################################################################
#Local
import logging
import os
import itertools

from databases import Databases

###############################################################################

class MatrixGenerator:
        
    KO      = 'KO_IDS.txt'
    PFAM    = 'PFAM_IDS.txt'
    TIGRFAM = 'TIGRFAM_IDS.txt'
    HYPOTHETICAL = 'HYPOTHETICAL'

    def __init__(self, annotation_type, clusters = None):
        '''
        Interpret which annotation type to write a matrix for.

        Parameters
        ----------
        annotation_type - String.
        '''
        self.annotation_type = annotation_type

        if self.annotation_type == self.KO:
            self.annotation_list = [x.strip() for x in open(os.path.join(Databases.IDS_DIR, self.KO))]
        elif self.annotation_type == self.PFAM:
            self.annotation_list = [x.strip() for x in open(os.path.join(Databases.IDS_DIR, self.PFAM))]
        elif self.annotation_type == self.TIGRFAM:
            self.annotation_list = [x.strip() for x in open(os.path.join(Databases.IDS_DIR, self.TIGRFAM))]
        elif self.annotation_type == self.HYPOTHETICAL:
            self.annotation_list = clusters

    def write_matrix(self, genomes_list, output_path):
        '''
        Writes a frequency matrix with of each annotation (rows) per sample (columns)

        Parameters
        ----------
        genomes_list        - list. List of Genome objects
        output_path         - string. Path to file to which the results are written.
        '''
        
        logging.info("    - Writing results to file: %s" % output_path)
        
        with open(output_path, 'w') as out_io:
            colnames = ['ID'] + [genome.name for genome in genomes_list]
            out_io.write('\t'.join(colnames) + '\n')

            genome_annotations = {genome.name:list(itertools.chain(*[sequence.all_annotations() for sequence in genome.sequences.values()]))
                                  for genome in genomes_list}

            for annotation in self.annotation_list:
                output_line = [annotation]
                for genome in genomes_list:

                    output_line.append(str(genome_annotations[genome.name].count(annotation)))

                out_io.write( '\t'.join(output_line) + '\n' )
