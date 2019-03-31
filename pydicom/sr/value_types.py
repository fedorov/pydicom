"""DICOM structured reporting content item value types."""
from enum import Enum

from pydicom.dataset import Dataset
from pydicom.valuerep import DA, TM, DT, PersonName

# FIXME: graphic data encoding?

class ValueTypes(Enum):

    CODE = 'CODE'
    COMPOSITE = 'COMPOSITE'
    CONTAINER = 'CONTAINER'
    DATE = 'DATE'
    DATETIME = 'DATETIME'
    IMAGE = 'IMAGE'
    NUM = 'NUM'
    PNAME = 'PNAME'
    SCOORD = 'SCOORD'
    SCOORD3D = 'SCOORD3D'
    TCOORD = 'TCOORD'
    TEXT = 'TEXT'
    TIME = 'TIME'
    UIDREF = 'UIDREF'
    WAVEFORM = 'WAVEFORM'


class GraphicTypes(Enum):

    CIRCLE = 'CIRCLE'
    ELLIPSE = 'ELLIPSE'
    ELLIPSOID = 'ELLIPSOID'
    MULTIPOINT = 'MULTIPOINT'
    POINT = 'POINT'
    POLYLINE = 'POLYLINE'


class GraphicTypes3D(Enum):

    CIRCLE = 'CIRCLE'
    ELLIPSE = 'ELLIPSE'
    ELLIPSOID = 'ELLIPSOID'
    MULTIPOINT = 'MULTIPOINT'
    POINT = 'POINT'
    POLYLINE = 'POLYLINE'
    POLYGON = 'POLYGON'


class TemporalRangeTypes(Enum):

    BEGIN = 'BEGIN'
    END = 'END'
    MULTIPOINT = 'MULTIPOINT'
    MULTISEGMENT = 'MULTISEGMENT'
    POINT = 'POINT'
    SEGMENT = 'SEGMENT'


class RelationshipTypes(Enum):

    CONTAINS = 'CONTAINS'
    HAS_ACQ_CONTENT = 'HAS ACQ CONTENT'
    HAS_CONCEPT_MOD = 'HAS CONCEPT MOD'
    HAS_OBS_CONTEXT = 'HAS OBS CONTEXT'
    HAS_PROPERTIES = 'HAS PROPERTIES'
    INFERRED_FROM = 'INFERRED FROM'
    SELECTED_FROM = 'SELECTED FROM'


class PixelOriginInterpretations(Enum):

    FRAME = 'FRAME'
    VOLUME = 'VOLUME'


class CodedConcept(Dataset):

    """Coded concept of a DICOM SR document content module attribute."""

    def __init__(self, value, meaning, scheme_designator, scheme_version=None):
        """
        Parameters
        ----------
        value: str
            the actual code
        meaning: str
            meaning of the code
        scheme_designator: str
            coding scheme designator
        scheme_version: Union[str, None], optional
            coding scheme version

        """
        super(CodedConcept, self).__init__()
        self.CodeValue = str(value)
        self.CodeMeaning = str(meaning)
        self.CodingSchemeDesignator = str(scheme_designator)
        if scheme_version is not None:
            self.CodingSchemeVersion = str(scheme_version)
        # TODO: Enhanced Code Sequence Macro Attributes

    def __eq__(self, item):
        if not isinstance(item, Dataset):
            return False
        if not hasattr(item, 'CodeValue'):
            return False
        equality_criteria = [
            self.CodeValue == item.CodeValue,
            self.CodingSchemeDesignator == item.CodingSchemeDesignator,
        ]
        if (hasattr(item, 'CodingSchemeVersion') and
                hasattr(self, 'CodingSchemeVersion')):
            equality_criteria.append(
                self.CodingSchemeVersion == item.CodingSchemeVersion
            )
        return all(equality_criteria)

    def to_json(self):
        """Serialize object in DICOM JSON format.

        Returns
        -------
        str
            serialized object

        """
        # TODO
        raise NotImplementedError()


class ContentItem(Dataset):

    """Abstract base class for a collection of attributes contained in the
    DICOM SR Document Content Module."""

    def __init__(self, value_type, name, relationship_type):
        """
        Parameters
        ----------
        value_type: str
            type of value encoded in a content item
        name: Union[pydicom.sr.value_types.CodedConcept, enum.Enum]
            coded name or an enumerated item representing a coded name
        relationship_type: Union[str, None]
            type of relationship with parent content item

        """
        super(ContentItem, self).__init__()
        value_type = ValueTypes(value_type)
        self.ValueType = value_type.value
        if isinstance(name, Enum):
            name = name.value
        if not isinstance(name, CodedConcept):
            raise TypeError('Concept name code must have type "CodedConcept".')
        self.ConceptNameCodeSequence = [name]
        if relationship_type is not None:
            relationship_type = RelationshipTypes(relationship_type)
            self.RelationshipType = relationship_type.value


class CodeContentItem(ContentItem):

    """DICOM SR document content item for value type CODE."""

    def __init__(self, name, value, relationship_type=None):
        """
        Parameters
        ----------
        name: pydicom.sr.value_types.CodedConcept
            concept name
        value: Union[pydicom.sr.value_types.CodedConcept, enum.Enum]
            coded value or an enumerated item representing a coded value
        relationship_type: Union[pydicom.sr.value_types.RelationshipTypes, str, None]
            type of relationship with parent content item

        """  # noqa
        super(CodeContentItem, self).__init__(
            ValueTypes.CODE, name, relationship_type
        )
        if isinstance(value, Enum):
            value = value.value
        if not isinstance(value, CodedConcept):
            raise TypeError('Argument "value" must have type "CodedConcept".')
        self.ConceptCodeSequence = [value]


class PnameContentItem(ContentItem):

    """DICOM SR document content item for value type PNAME."""

    def __init__(self, name, value, relationship_type=None):
        """
        Parameters
        ----------
        name: pydicom.sr.value_types.CodedConcept
            concept name
        value: str
            name of the person
        relationship_type: Union[pydicom.sr.value_types.RelationshipTypes, str, None]
            type of relationship with parent content item

        """  # noqa
        super(PnameContentItem, self).__init__(
            ValueTypes.PNAME, name, relationship_type
        )
        self.PersonName = PersonName(value)


class TextContentItem(ContentItem):

    """DICOM SR document content item for value type TEXT."""

    def __init__(self, name, value, relationship_type=None):
        """
        Parameters
        ----------
        name: pydicom.sr.value_types.CodedConcept
            concept name
        value: str
            description of the concept in free text
        relationship_type: Union[pydicom.sr.value_types.RelationshipTypes, str]
            type of relationship with parent content item

        """
        super(TextContentItem, self).__init__(
            ValueTypes.TEXT, name, relationship_type
        )
        self.TextValue = str(value)


class TimeContentItem(ContentItem):

    """DICOM SR document content item for value type TIME."""

    def __init__(self, name, value, relationship_type=None):
        """
        Parameters
        ----------
        name: pydicom.sr.value_types.CodedConcept
            concept name
        value: pydicom.valuerep.TM
            time
        relationship_type: Union[pydicom.sr.value_types.RelationshipTypes, str, None]
            type of relationship with parent content item

        """  # noqa
        super(TimeContentItem, self).__init__(
            ValueTypes.TIME, name, relationship_type
        )
        self.Time = TM(value)


class DateContentItem(ContentItem):

    """DICOM SR document content item for value type DATE."""

    def __init__(self, name, value, relationship_type=None):
        """
        Parameters
        ----------
        name: pydicom.sr.value_types.CodedConcept
            concept name
        value: Union[pydicom.valuerep.DA, str]
            date
        relationship_type: Union[pydicom.sr.value_types.RelationshipTypes, str, None]
            type of relationship with parent content item

        """  # noqa
        super(DateContentItem, self).__init__(
            ValueTypes.DATE, name, relationship_type
        )
        self.Date = DA(value)


class DateTimeContentItem(ContentItem):

    """DICOM SR document content item for value type DATETIME."""

    def __init__(self, name, value, relationship_type=None):
        """
        Parameters
        ----------
        name: pydicom.sr.value_types.CodedConcept
            concept name
        value: Union[pydicom.valuerep.DT, str]
            datetime
        relationship_type: Union[pydicom.sr.value_types.RelationshipTypes, str, None]
            type of relationship with parent content item

        """  # noqa
        super(DateTimeContentItem, self).__init__(
            ValueTypes.DATETIME, name, relationship_type
        )
        self.DateTime = DT(value)


class UIDRefContentItem(ContentItem):

    """DICOM SR document content item for value type UIDREF."""

    def __init__(self, name, value, relationship_type=None):
        """
        Parameters
        ----------
        name: pydicom.sr.value_types.CodedConcept
            concept name
        value: Union[pydicom.uid.UID, str]
            unique identifier
        relationship_type: Union[pydicom.sr.value_types.RelationshipTypes, str, None]
            type of relationship with parent content item

        """  # noqa
        super(UIDRefContentItem, self).__init__(
            ValueTypes.UIDREF, name, relationship_type
        )
        self.UID = str(value)


class NumContentItem(ContentItem):

    """DICOM SR document content item for value type NUM."""

    def __init__(self, name, value=None, unit=None, qualifier=None,
                 relationship_type=None):
        """
        Parameters
        ----------
        name: pydicom.sr.value_types.CodedConcept
            concept name
        value: Union[int, float], optional
            numeric value
        unit: Union[pydicom.sr.value_types.CodedConcept, None], optional
            coded units of measurement
        qualifier: Union[pydicom.sr.value_types.CodedConcept, None], optional
            qualification of numeric value or as an alternative to
            numeric value
        relationship_type: Union[pydicom.sr.value_types.RelationshipTypes, str, None], optional
            type of relationship with parent content item

        Note
        ----
        Either `value` and `unit` or `qualifier` must be specified.

        """ # noqa
        super(NumContentItem, self).__init__(
            ValueTypes.NUM, name, relationship_type
        )
        if value is not None:
            self.MeasuredValueSequence = []
            measured_value_sequence_item = Dataset()
            if not isinstance(value, (int, float, )):
                raise TypeError(
                    'Argument "value" must have type "int" or "float".'
                )
            measured_value_sequence_item.NumericValue = value
            if isinstance(value, float):
                measured_value_sequence_item.FloatingPointValue = value
            if isinstance(unit, Enum):
                unit = unit.value
            if not isinstance(unit, CodedConcept):
                raise TypeError(
                    'Argument "unit" must have type "CodedConcept".'
                )
            measured_value_sequence_item.MeasurementUnitsCodeSequence = [unit]
            self.MeasuredValueSequence.append(measured_value_sequence_item)
        elif qualifier is not None:
            if isinstance(qualifier, Enum):
                qualifier = qualifier.value
            if not isinstance(qualifier, CodedConcept):
                raise TypeError(
                    'Argument "qualifier" must have type "CodedConcept".'
                )
            self.NumericValueQualifierCodeSequence = [qualifier]
        else:
            raise ValueError(
                'Either "value" or "qualifier" must be specified upon '
                'creation of NumContentItem.'
            )


class ContainerContentItem(ContentItem):

    """DICOM SR document content item for value type CONTAINER."""

    def __init__(self, name, relationship_type=None,
                 is_content_continuous=True, template_id=None):
        """
        Parameters
        ----------
        name: pydicom.sr.value_types.CodedConcept
            concept name
        relationship_type: Union[str, None], optional
            type of relationship with parent content item
        is_content_continous: bool, optional
            whether contained content items are logically linked in a
            continuous manner or separate items (default: ``True``)
        template_id: Union[str, None], optional
            SR template identifier

        """
        super(ContainerContentItem, self).__init__(
            ValueTypes.CONTAINER, name, relationship_type
        )
        if is_content_continuous:
            self.ContinuityOfContent = 'CONTINUOUS'
        else:
            self.ContinuityOfContent = 'SEPARATE'
        if template_id is not None:
            if not template_id.startswith('TID'):
                raise ValueError(
                    'Invalid template identifier: "{}"'.format(template_id)
                )
            item = Dataset()
            item.MappingResource = 'DCMR'
            item.TemplateIdentifier = str(template_id)
            self.ContentTemplateSequence = [item]


class CompositeContentItem(ContentItem):

    """DICOM SR document content item for value type COMPOSITE."""

    def __init__(self, name,
                 referenced_sop_class_uid, referenced_sop_instance_uid,
                 relationship_type=None):
        """
        Parameters
        ----------
        name: pydicom.sr.value_types.CodedConcept
            concept name
        relationship_type: Union[pydicom.sr.value_types.RelationshipTypes, str]
            type of relationship with parent content item
        referenced_sop_class_uid: Union[pydicom.uid.UID, str]
            SOP Class UID of the referenced object
        referenced_sop_instance_uid: Union[pydicom.uid.UID, str]
            SOP Instance UID of the referenced object
        relationship_type: Union[pydicom.sr.value_types.RelationshipTypes, str, None], optional
            type of relationship with parent content item

        """  # noqa
        super(CompositeContentItem, self).__init__(
            ValueTypes.COMPOSITE, name, relationship_type
        )
        item = Dataset()
        item.ReferencedSOPClassUID = str(referenced_sop_class_uid)
        item.ReferencedSOPInstanceUID = str(referenced_sop_instance_uid)
        self.ReferenceSOPSequence = [item]


class ImageContentItem(ContentItem):

    """DICOM SR document content item for value type IMAGE."""

    def __init__(self, name,
                 referenced_sop_class_uid, referenced_sop_instance_uid,
                 referenced_frame_number=None, referenced_segment_number=None,
                 relationship_type=None):
        """
        Parameters
        ----------
        name: pydicom.sr.value_types.CodedConcept
            concept name
        referenced_sop_class_uid: Union[pydicom.uid.UID, str]
            SOP Class UID of the referenced image object
        referenced_sop_instance_uid: Union[pydicom.uid.UID, str]
            SOP Instance UID of the referenced image object
        referenced_frame_number: Union[int, List[int], None], optional
            number of frame(s) to which the reference applies in case of a
            multi-frame image
        referenced_segment_number: Union[int, List[int], None], optional
            number of segment(s) to which the refernce applies in case of a
            segmentation image
        relationship_type: Union[pydicom.sr.value_types.RelationshipTypes, str, None], optional
            type of relationship with parent content item

        """  # noqa
        super(ImageContentItem, self).__init__(
            ValueTypes.IMAGE, name, relationship_type
        )
        item = Dataset()
        item.ReferencedSOPClassUID = str(referenced_sop_class_uid)
        item.ReferencedSOPInstanceUID = str(referenced_sop_instance_uid)
        if referenced_frame_number is not None:
            item.ReferencedFrameNumber = referenced_frame_number
        if referenced_segment_number is not None:
            item.ReferencedSegmentNumber = referenced_segment_number
        self.ReferencedSOPSequence = [item]


class ScoordContentItem(ContentItem):

    """DICOM SR document content item for value type SCOORD.

    Note
    ----
    Spatial coordinates are defined in image space and have pixel units.

    """

    def __init__(self, name, graphic_type, graphic_data,
                 pixel_origin_interpretation, fiducial_uid=None,
                 relationship_type=None):
        """
        Parameters
        ----------
        name: pydicom.sr.value_types.CodedConcept
            concept name
        graphic_type: Union[pydicom.sr.value_types.GraphicTypes, str]
            name of the graphic type
        graphic_data: Union[List[List[Union[int, float]]], List[Union[int, float]]]
            ordered (column, row) coordinate pairs
        pixel_origin_interpretation: Union[pydicom.sr.value_types.PixelOriginInterpretations, str]
            whether pixel coordinates specified by `graphic_data` are defined
            relative to the total pixel matrix
            (``pydicom.sr.value_types.PixelOriginInterpretations.VOLUME``) or
            relative to an individual frame
            (``pydicom.sr.value_types.PixelOriginInterpretations.FRAME``)
        fiducial_uid: Union[pydicom.uid.UID, str, None], optional
            unique identifier for the content item
        relationship_type: Union[pydicom.sr.value_types.RelationshipTypes, str, None], optional
            type of relationship with parent content item

        """  # noqa
        super(ScoordContentItem, self).__init__(
            ValueTypes.SCOORD, name, relationship_type
        )
        graphic_type = GraphicTypes(graphic_type)
        pixel_origin_interpretation = PixelOriginInterpretations(
            pixel_origin_interpretation
        )
        self.GraphicType = graphic_type.value

        def is_point(coordinate):
            try:
                return all([
                    isinstance(coordinate, (list, tuple, )),
                    len(coordinate) == 2,
                    all([isinstance(c, (int, float, )) for c in coordinate]),
                ])
            except IndexError:
                return False

        if graphic_type == GraphicTypes.POINT:
            if not is_point(graphic_data):
                raise ValueError(
                    'Graphic data of a scoord of graphic type "POINT" '
                    'must be a single (column row) pair in two-dimensional '
                    'image coordinate space.'
                )
            # Flatten list of coordinate pairs
            self.GraphicData = [
                float(coordinate) for coordinate in graphic_data
            ]
        else:
            # TODO: This may be expensive for large lists.
            are_all_points = all([
                is_point(coordinates) for coordinates in graphic_data
            ])
            if graphic_type == GraphicTypes.CIRCLE:
                if len(graphic_data) != 2 or not(are_all_points):
                    raise ValueError(
                        'Graphic data of a scoord of graphic type "CIRCLE" '
                        'must be two (column, row) pairs in two-dimensional '
                        'image coordinate space.'
                    )
            elif graphic_type == GraphicTypes.ELLIPSE:
                if len(graphic_data) != 4 or not(are_all_points):
                    raise ValueError(
                        'Graphic data of a scoord of graphic type "ELLIPSE" '
                        'must be four (column, row) pairs in two-dimensional '
                        'image coordinate space.'
                    )
            elif graphic_type == GraphicTypes.ELLIPSOID:
                if len(graphic_data) != 6 or not(are_all_points):
                    raise ValueError(
                        'Graphic data of a scoord of graphic type "ELLIPSOID" '
                        'must be six (column, row) pairs in two-dimensional '
                        'image coordinate space.'
                    )
            else:
                if not len(graphic_data) > 1 or not(are_all_points):
                    raise ValueError(
                        'Graphic data of a scoord must be multiple '
                        '(column, row) pairs in two-dimensional image '
                        'coordinate space.'
                    )
            # Flatten list of coordinate pairs
            self.GraphicData = [
                float(coordinate) for pair in graphic_data
                for coordinate in pair
            ]
        self.PixelOriginInterpretation = pixel_origin_interpretation.value
        if fiducial_uid is not None:
            self.FiducialUID = fiducial_uid


class Scoord3DContentItem(ContentItem):

    """DICOM SR document content item for value type SCOORD3D.

    Note
    ----
    Spatial coordinates are defined in the patient or specimen-based coordinate
    system and have milimeter unit.

    """

    def __init__(self, name, graphic_type, graphic_data,
                 frame_of_reference_uid, fiducial_uid=None,
                 relationship_type=None):
        """
        Parameters
        ----------
        name: pydicom.sr.value_types.CodedConcept
            concept name
        graphic_type: Union[pydicom.sr.value_types.GraphicTypes, str]
            name of the graphic type
        graphic_data: List[List[int, float]]
            ordered set of (x, y, z) coordinate triplets
        frame_of_reference_uid: Union[pydicom.uid.UID, str]
            unique identifier of the frame of reference within which the
            coordinates are defined
        fiducial_uid: Union[str, None], optional
            unique identifier for the content item
        relationship_type: Union[pydicom.sr.value_types.RelationshipTypes, str, None], optional
            type of relationship with parent content item

        """  # noqa
        super(Scoord3DContentItem, self).__init__(
            ValueTypes.SCOORD3D, name, relationship_type
        )
        graphic_type = GraphicTypes3D(graphic_type)
        self.GraphicType = graphic_type.value

        def is_point(coordinate):
            try:
                return all([
                    isinstance(coordinate, (list, tuple, )),
                    len(coordinate) == 3,
                    all([isinstance(c, (int, float, )) for c in coordinate]),
                ])
            except IndexError:
                return False

        if graphic_type == GraphicTypes3D.POINT:
            if not is_point(graphic_data):
                raise ValueError(
                    'Graphic data of a scoord 3D of graphic type "POINT" '
                    'must be a single point in three-dimensional patient or '
                    'slide coordinate space in form of a (x, y, z) triplet.'
                )
            self.GraphicData = [
                float(coordinate) for coordiante in graphic_data
            ]
        else:
            are_all_points = all([
                is_point(coordinates) for coordinates in graphic_data
            ])
            if graphic_type == GraphicTypes3D.CIRCLE:
                if len(graphic_data) != 2 or not(are_all_points):
                    raise ValueError(
                        'Graphic data of a 3D scoord of graphic type "CIRCLE" '
                        'must be (x, y, z) triplets in three-dimensional '
                        'patient or slide coordinate space.'
                    )
            elif graphic_type == GraphicTypes3D.ELLIPSE:
                if len(graphic_data) != 4 or not(are_all_points):
                    raise ValueError(
                        'Graphic data of a 3D scoord of graphic type "ELLIPSE" '
                        'must be four (x, y, z) triplets in three-dimensional '
                        'patient or slide coordinate space.'
                    )
            elif graphic_type == GraphicTypes3D.ELLIPSOID:
                if len(graphic_data) != 6 or not(are_all_points):
                    raise ValueError(
                        'Graphic data of a 3D scoord of graphic type '
                        '"ELLIPSOID" must be six (x, y, z) triplets in '
                        'three-dimensional patient or slide coordinate space.'
                    )
            else:
                if not len(graphic_data) > 1 or not(are_all_points):
                    raise ValueError(
                        'Graphic data of a 3D scoord must be multiple '
                        '(x, y, z) triplets in three-dimensional patient or '
                        'slide coordinate space.'
                    )
            # Flatten list of coordinate triplets
            self.GraphicData = [
                float(coordinate) for triplet in graphic_data
                for coordinate in triplet
            ]
        self.FrameOfReferenceUID = frame_of_reference_uid
        if fiducial_uid is not None:
            self.FiducialUID = fiducial_uid


class TcoordContentItem(ContentItem):

    """DICOM SR document content item for value type TCOORD."""

    def __init__(self, name, referenced_sample_positions,
                 referenced_time_offsets, referenced_date_time=None,
                 relationship_type=None):
        """
        Parameters
        ----------
        name: pydicom.sr.value_types.CodedConcept
            concept name
        temporal_range_type: Union[pydicom.sr.value_types.TemporalRangeTypes, str]
            name of the temporal range type
        referenced_sample_positions: Union[List[int], None], optional
            one-based relative sample position of acquired time points
            within the time series
        referenced_time_offsets: Union[List[float], None], optional
            seconds after start of the acquisition of the time series
        referenced_date_time: Union[List[datetime.datetime], None], optional
            absolute time points
        relationship_type: Union[pydicom.sr.value_types.RelationshipTypes, str, None], optional
            type of relationship with parent content item

        """  # noqa
        super(TcoordContentItem, self).__init__(
            ValueTypes.TSCOORD, name, relationship_type
        )
        temporal_range_type = TemporalRangeTypes(temporal_range_type)
        if referenced_sample_positions is not None:
            self.ReferencedSamplePositions = [
                int(v) for v in referenced_sample_positions
            ]
        elif referenced_time_offsets is not None:
            self.ReferencedTimeOffsets = [
                float(v) for v in referenced_time_offsets
            ]
        elif referenced_date_time is not None:
            self.ReferencedDateTime = [
                DT(v) for v in referenced_date_time
            ]
        else:
            raise ValueError(
                'One of the following arguments is required: "{}"'.format(
                    '", "'.join([
                        'referenced_sample_positions',
                        'referenced_time_offsets',
                        'referenced_date_time'
                    ])
                )
            )
