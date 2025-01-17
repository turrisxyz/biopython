# Copyright 2022 by Michiel de Hoon.  All rights reserved.
#
# This file is part of the Biopython distribution and governed by your
# choice of the "Biopython License Agreement" or the "BSD 3-Clause License".
# Please see the LICENSE file that should have been included as part of this
# package.
"""Bio.Align support for aligned FASTA files.

Aligned FASTA files are FASTA files in which alignment gaps in a sequence are
represented by dashes. Each sequence line in an aligned FASTA should have the
same length.
"""
from Bio.Align import Alignment
from Bio.Align import interfaces
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio import BiopythonExperimentalWarning

import warnings

warnings.warn(
    "Bio.Align.fasta is an experimental module which may undergo "
    "significant changes prior to its future official release.",
    BiopythonExperimentalWarning,
)


class AlignmentWriter(interfaces.AlignmentWriter):
    """Alignment file writer for the aligned FASTA file format."""

    def __init__(self, target):
        """Create an AlignmentWriter object.

        Arguments:
         - target    - output stream or file name

        """
        super().__init__(target, mode="w")

    def format_alignment(self, alignment):
        """Return a string with the alignment in aligned FASTA format."""
        if not isinstance(alignment, Alignment):
            raise TypeError("Expected an Alignment object")
        lines = []
        for sequence, line in zip(alignment.sequences, alignment):
            lines.append(f">{sequence.id} {sequence.description}")
            lines.append(line)
        return "\n".join(lines)


class AlignmentIterator(interfaces.AlignmentIterator):
    """Alignment iterator for aligned FASTA files.

    An aligned FASTA file contains one multiple alignment. Alignment gaps are
    represented by dashes in the sequence lines. Header lines start with '>'
    followed by the name of the sequence, and optionally a description.
    """

    def __init__(self, source):
        """Create an AlignmentIterator object.

        Arguments:
         - source   - input data or file name

        """
        super().__init__(source, mode="t", fmt="FASTA")

    def parse(self, stream):
        """Parse the next alignment from the stream."""
        names = []
        descriptions = []
        lines = []
        for line in stream:
            if line.startswith(">"):
                parts = line[1:].rstrip().split(None, 1)
                try:
                    name, description = parts
                except ValueError:
                    name = parts[0]
                    description = None
                names.append(name)
                descriptions.append(description)
                lines.append("")
            else:
                lines[-1] += line.strip()
        if not lines:
            raise ValueError("Empty file.")
        coordinates = Alignment.infer_coordinates(lines)
        records = []
        for name, description, line in zip(names, descriptions, lines):
            line = line.replace("-", "")
            sequence = Seq(line)
            if description is None:
                record = SeqRecord(sequence, name)
            else:
                record = SeqRecord(sequence, name, description=description)
            records.append(record)
        alignment = Alignment(records, coordinates)
        yield alignment
