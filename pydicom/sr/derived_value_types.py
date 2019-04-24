"""Custom content items derived from DICOM value types."""
from pydicom.sr.coding import Code, CodedConcept
from pydicom.sr.value_types import (
    CodeContentItem, CompositeContentItem, ContentSequence, GraphicTypes,
    GraphicTypes3D, ImageContentItem, NumContentItem,
    PixelOriginInterpretations, RelationshipTypes, ScoordContentItem,
    Scoord3DContentItem, UIDRefContentItem,
)


class LongitudinalTemporalOffsetFromEventContentItem(NumContentItem):

    """Content item for Longitudinal Temporal Offset From Event."""

    def __init__(self, value, unit, event_type):
        """
        Parameters
        ----------
        value: Union[int, float, None], optional
            offset in time from a particular event of significance
        unit: Union[pydicom.sr.coding.CodedConcept, pydicom.sr.coding.Code, None], optional
            unit of time, e.g., "Days" or "Seconds"
        event_type: Union[pydicom.sr.coding.CodedConcept, pydicom.sr.coding.Code, None], optional
            type of event to which offset is relative,
            e.g., "Baseline" or "Enrollment"

        """
        super(LongitudinalTemporalOffsetFromEventContentItem, self).__init__(
            name=CodedConcept(
                value='128740',
                meaning='Longitudinal Temporal Offset from Event',
                scheme_designator='DCM'
            ),
            value=value,
            unit=unit,
            relationship_type=RelationshipTypes.HAS_OBS_CONTEXT
        )
        event_type_item = CodeContentItem(
            name=CodedConcept(
                value='128741',
                meaning='Longitudinal Temporal Event Type',
                scheme_designator='DCM'
            ),
            value=event_type,
            relationship_type=RelationshipTypes.HAS_CONCEPT_MOD
        )
        self.ContentSequence = ContentSequence([event_type_item])


class SourceImageForRegionContentItem(ImageContentItem):

    """Content item for Source Image for Region"""

    def __init__(self, referenced_sop_class_uid, referenced_sop_instance_uid,
                 referenced_frame_numbers=None):
        """
        Parameters
        ----------
        referenced_sop_class_uid: Union[pydicom.uid.UID, str]
            SOP Class UID of the referenced image object
        referenced_sop_instance_uid: Union[pydicom.uid.UID, str]
            SOP Instance UID of the referenced image object
        referenced_frame_numbers: Union[List[int], None], optional
            numbers of the frames to which the reference applies in case the
            referenced image is a multi-frame image

        """
        super(SourceImageForRegionContentItem, self).__init__(
            name=CodedConcept(
                value='121324',
                meaning='Source Image',
                scheme_designator='DCM'
            ),
            referenced_sop_class_uid=referenced_sop_class_uid,
            referenced_sop_instance_uid=referenced_sop_instance_uid,
            referenced_frame_numbers=referenced_frame_numbers,
            relationship_type=RelationshipTypes.SELECTED_FROM
        )


class SourceImageForSegmentationContentItem(ImageContentItem):

    """Content item for Source Image for Segmentation"""

    def __init__(self, referenced_sop_class_uid, referenced_sop_instance_uid,
                 referenced_frame_numbers=None):
        """
        Parameters
        ----------
        referenced_sop_class_uid: Union[pydicom.uid.UID, str]
            SOP Class UID of the referenced image object
        referenced_sop_instance_uid: Union[pydicom.uid.UID, str]
            SOP Instance UID of the referenced image object
        referenced_frame_numbers: Union[List[int], None], optional
            numbers of the frames to which the reference applies in case the
            referenced image is a multi-frame image

        """
        super(SourceImageForSegmentationContentItem, self).__init__(
            name=CodedConcept(
                value='121233',
                meaning='Source Image for Segmentation',
                scheme_designator='DCM'
            ),
            referenced_sop_class_uid=referenced_sop_class_uid,
            referenced_sop_instance_uid=referenced_sop_instance_uid,
            referenced_frame_numbers=referenced_frame_numbers,
            relationship_type=RelationshipTypes.CONTAINS
        )


class SourceSeriesForSegmentationContentItem(UIDRefContentItem):

    """Content item for Source Series for Segmentation"""

    def __init__(self, referenced_series_instance_uid):
        """
        Parameters
        ----------
        referenced_series_instance_uid: Union[pydicom.uid.UID, str]
            Series Instance UID

        """
        super(SourceImageForSegmentationContentItem, self).__init__(
            name=CodedConcept(
                value='121232',
                meaning='Source Series for Segmentation',
                scheme_designator='DCM'
            ),
            value=referenced_series_instance_uid,
            relationship_type=RelationshipTypes.CONTAINS
        )


class ReferencedRegionContentItem(ScoordContentItem):

    """Content item for a refrenced region of interest"""

    def __init__(self, graphic_type, graphic_data, source_image,
                 pixel_origin_interpretation=PixelOriginInterpretations.VOLUME):
        """
        Parameters
        ----------
        graphic_type: Union[pydicom.sr.value_types.GraphicTypes, str]
            name of the graphic type
        graphic_data: List[List[int]]
            ordered set of (row, column) coordinate pairs
        source_image: pydicom.sr.template.SourceImageForRegionContentItem
            source image to which `graphic_data` relate
        pixel_origin_interpretation: Union[pydicom.sr.value_types.PixelOriginInterpretations, str, None], optional
            whether pixel coordinates specified by `graphic_data` are defined
            relative to the total pixel matrix
            (``pydicom.sr.value_types.PixelOriginInterpretations.VOLUME``) or
            relative to an individual frame
            (``pydicom.sr.value_types.PixelOriginInterpretations.FRAME``)
            of the source image
            (default: ``pydicom.sr.value_types.PixelOriginInterpretations.VOLUME``)

        """  # noqa
        graphic_type = GraphicTypes(graphic_type)
        if graphic_type == GraphicTypes.MULTIPOINT:
            raise ValueError(
                'Graphic type "MULTIPOINT" is not valid for region.'
            )
        if not isinstance(source_image, SourceImageForRegionContentItem):
            raise TypeError(
                'Argument "source_image" must have type '
                'SourceImageForRegionContentItem.'
            )
        if pixel_origin_interpretation == PixelOriginInterpretations.FRAME:
            if (not hasattr(source_image, 'ReferencedFrameNumber') or
                source_image.ReferencedFrameNumber is None):
                raise ValueError(
                    'Frame number of source image must be specified when value '
                    'of argument "pixel_origin_interpretation" is "FRAME".'
                )
        super(ReferencedRegionContentItem, self).__init__(
            name=CodedConcept(
                value='111030',
                meaning='Image Region',
                scheme_designator='DCM'
            ),
            graphic_type=graphic_type,
            graphic_data=graphic_data,
            pixel_origin_interpretation=pixel_origin_interpretation,
            relationship_type=RelationshipTypes.CONTAINS
        )
        self.ContentSequence = [source_image]


class ReferencedVolumeSurfaceContentItem(Scoord3DContentItem):

    """Referenced volume surface"""

    def __init__(self, graphic_type, graphic_data, frame_of_reference_uid,
                 source_images=None, source_series=None):
        """
        Parameters
        ----------
        graphic_type: Union[pydicom.sr.value_types.GraphicTypes, str]
            name of the graphic type
        graphic_data: List[List[int]]
            ordered set of (row, column, frame) coordinate pairs
        frame_of_reference_uid: Union[pydicom.uid.UID, str]
            unique identifier of the frame of reference within which the
            coordinates are defined
        source_images: Union[List[pydicom.sr.templates.SourceImageForSegmentationContentItem], None], optional
            source images for segmentation
        source_series: Union[pydicom.sr.templates.SourceSeriesForSegmentationContentItem, None], optional
            source series for segmentation

        Note
        ----
        Either one or more source images or one source series must be provided.

        """
        graphic_type = GraphicTypes3D(graphic_type)
        if graphic_type != GraphicTypes3D.ELLIPSOID:
            raise ValueError(
                'Graphic type for volume surface must be "ELLIPSOID".'
            )
        super(ReferencedVolumeSurfaceContentItem, self).__init__(
            name=CodedConcept(
                value='121231',
                meaning='Volume Surface',
                scheme_designator='DCM'
            ),
            frame_of_reference_uid=frame_of_reference_uid,
            graphic_type=graphic_type,
            graphic_data=graphic_data,
            relationship_type=RelationshipTypes.CONTAINS
        )
        self.ContentSequence = ContentSequence()
        if source_images is not None:
            for image in source_images:
                if not isinstance(image, SourceImageForSegmentationContentItem):
                    raise TypeError(
                        'Items of argument "source_image" must have type '
                        'SourceImageForSegmentationContentItem.'
                    )
                self.ContentSequence.append(image)
        elif source_series is not None:
            if not isinstance(source_series,
                              SourceSeriesForSegmentationContentItem):
                raise TypeError(
                    'Argument "source_series" must have type '
                    'SourceSeriesForSegmentationContentItem.'
                )
            self.ContentSequence.append(source_series)
        else:
            raise ValueError(
                'One of the following two arguments must be provided: '
                '"source_images" or "source_series".'
            )


class ReferencedRealWorldValueMapContentItem(CompositeContentItem):

    """Referenced real world value map"""

    def __init__(self, referenced_sop_instance_uid):
        """
        Parameters
        ----------
        referenced_sop_instance_uid: Union[pydicom.uid.UID, str]
            SOP Instance UID of the referenced object

        """
        super(ReferencedRealWorldValueMapContentItem, self).__init__(
            name=CodedConcept(
                value='126100',
                meaning='Real World Value Map used for measurement',
                scheme_designator='DCM'
            ),
            referenced_sop_class_uid='1.2.840.10008.5.1.4.1.1.67',
            referenced_sop_instance_uid=referenced_sop_instance_uid,
            relationship_type=RelationshipTypes.CONTAINS
        )


class FindingSiteContentItem(CodeContentItem):

    def __init__(self, anatomic_location, laterality=None,
                 topographical_modifier=None):
        """
        Parameters
        ----------
        anatomic_location: Union[pydicom.sr.coding.CodedConcept, pydicom.sr.coding.Code, None], optional
            coded anatomic location (region or structure)
        laterality: Union[pydicom.sr.coding.CodedConcept, pydicom.sr.coding.Code, None], optional
            coded laterality
            (see CID 244 "Laterality" for options)
        topographical_modifier: Union[pydicom.sr.coding.CodedConcept, pydicom.sr.coding.Code, None], optional
            coded modifier value for anatomic location

        """  # noqa
        super(FindingSiteContentItem, self).__init__(
            name=CodedConcept(
                value='G-C0E3',
                meaning='Finding Site',
                scheme_designator='SRT'
            ),
            value=anatomic_location,
            relationship_type=RelationshipTypes.HAS_CONCEPT_MOD
        )
        self.ContentSequence = ContentSequence()
        if laterality is not None:
            laterality_item = CodeContentItem(
                name=CodedConcept(
                    value='G-C171',
                    meaning='Laterality',
                    scheme_designator='SRT'
                ),
                value=laterality,
                relationship_type=RelationshipTypes.HAS_CONCEPT_MOD
            )
            self.ContentSequence.append(laterality_item)
        if topographical_modifier is not None:
            modifier_item = CodeContentItem(
                name=CodedConcept(
                    value='G-A1F8',
                    meaning='Topographical Modifier',
                    scheme_designator='SRT'
                ),
                value=topographical_modifier,
                relationship_type=RelationshipTypes.HAS_CONCEPT_MOD
            )
            self.ContentSequence.append(modifier_item)

