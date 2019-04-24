import unittest

import pytest

from pydicom.dataset import Dataset
from pydicom.sr import codes
from pydicom.sr.document import Comprehensive3DSR
from pydicom.sr.templates import (
    DEFAULT_LANGUAGE,
    DeviceObserverIdentifyingAttributes,
    Measurement,
    MeasurementReport,
    ObservationContext,
    ObserverContext,
    PersonObserverIdentifyingAttributes,
    PlanarROIMeasurementsAndQualitativeEvaluations,
    ROIMeasurements,
    SubjectContext,
    SubjectContextSpecimen,
    TrackingIdentifier,
    VolumetricROIMeasurementsAndQualitativeEvaluations,
)
from pydicom.sr.coding import CodedConcept
from pydicom.sr.value_types import (
    GraphicTypes,
    GraphicTypes3D,
    NumContentItem,
)
from pydicom.sr.content_items import (
    FindingSite,
    ImageRegion,
    VolumeSurface,
    SourceImageForRegion,
    SourceImageForSegmentation,
)
from pydicom.uid import generate_uid
from pydicom.valuerep import DS


class TestObservationContext(unittest.TestCase):

    def setUp(self):
        super(TestObservationContext, self).setUp()
        self._person_name = 'Foo Bar'
        self._device_uid = generate_uid()
        self._specimen_uid = generate_uid()
        self._observer_person_context = ObserverContext(
            observer_type=codes.cid270.Person,
            observer_identifying_attributes=PersonObserverIdentifyingAttributes(
                name=self._person_name
            )
        )
        self._observer_device_context = ObserverContext(
            observer_type=codes.cid270.Device,
            observer_identifying_attributes=DeviceObserverIdentifyingAttributes(
                uid=self._device_uid
            )
        )
        self._subject_context = SubjectContext(
            subject_class=codes.cid271.Specimen,
            subject_class_specific_context=SubjectContextSpecimen(
                uid=self._specimen_uid
            )
        )
        self._observation_context = ObservationContext(
            observer_person_context=self._observer_person_context,
            observer_device_context=self._observer_device_context,
            subject_context=self._subject_context
        )

    def test_observer_context(self):
        # person
        assert len(self._observer_person_context) == 2
        item = self._observer_person_context[0]
        assert item.ConceptNameCodeSequence[0].CodeValue == '121005'
        assert item.ConceptCodeSequence[0] == codes.cid270.Person
        item = self._observer_person_context[1]
        assert item.ConceptNameCodeSequence[0].CodeValue == '121008'
        assert item.TextValue == self._person_name
        # device
        assert len(self._observer_device_context) == 2
        item = self._observer_device_context[0]
        assert item.ConceptNameCodeSequence[0].CodeValue == '121005'
        assert item.ConceptCodeSequence[0] == codes.cid270.Device
        item = self._observer_device_context[1]
        assert item.ConceptNameCodeSequence[0].CodeValue == '121012'
        assert item.UID == self._device_uid

    def test_subject_context(self):
        assert len(self._subject_context) == 2
        item = self._subject_context[0]
        assert item.ConceptNameCodeSequence[0].CodeValue == '121024'
        assert item.ConceptCodeSequence[0] == codes.cid271.Specimen
        item = self._subject_context[1]
        assert item.ConceptNameCodeSequence[0].CodeValue == '121039'
        assert item.UID == self._specimen_uid

    def test_content_length(self):
        assert len(self._observation_context) == 6


class TestFindingSiteOptional(unittest.TestCase):

    def setUp(self):
        super(TestFindingSiteOptional, self).setUp()
        self._location = codes.cid7151.LobeOfLung
        self._laterality = codes.cid244.Right
        self._modifier = codes.cid2.Apical
        self._finding_site = FindingSite(
            anatomic_location=self._location,
            laterality=self._laterality,
            topographical_modifier=self._modifier
        )

    def test_finding_site(self):
        item = self._finding_site
        assert item.ConceptNameCodeSequence[0].CodeValue == 'G-C0E3'
        assert item.ConceptCodeSequence[0] == self._location
        assert len(item.ContentSequence) == 2

    def test_laterality(self):
        item = self._finding_site.ContentSequence[0]
        assert item.ConceptNameCodeSequence[0].CodeValue == 'G-C171'
        assert item.ConceptCodeSequence[0] == self._laterality

    def test_topographical_modifier(self):
        item = self._finding_site.ContentSequence[1]
        assert item.ConceptNameCodeSequence[0].CodeValue == 'G-A1F8'
        assert item.ConceptCodeSequence[0] == self._modifier


class TestFindingSite(unittest.TestCase):

    def setUp(self):
        super(TestFindingSite, self).setUp()
        self._location = codes.cid6300.RightAnteriorMiddlePeripheralZoneOfProstate
        self._finding_site = FindingSite(
            anatomic_location=self._location
        )

    def test_finding_site(self):
        item = self._finding_site
        assert item.ConceptNameCodeSequence[0].CodeValue == 'G-C0E3'
        assert item.ConceptCodeSequence[0] == self._location
        assert len(item.ContentSequence) == 0


class TestTrackingIdentifierOptional(unittest.TestCase):

    def setUp(self):
        super(TestTrackingIdentifierOptional, self).setUp()
        self._uid = generate_uid()
        self._identifier = 'prostate zone size measurements'
        self._tracking_identifier = TrackingIdentifier(
            uid=self._uid,
            identifier=self._identifier
        )

    def test_identifier(self):
        item = self._tracking_identifier[0]
        assert item.ConceptNameCodeSequence[0].CodeValue == '112039'
        assert item.TextValue == self._identifier

    def test_uid(self):
        item = self._tracking_identifier[1]
        assert item.ConceptNameCodeSequence[0].CodeValue == '112040'
        assert item.UID == self._uid


class TestTrackingIdentifier(unittest.TestCase):

    def setUp(self):
        super(TestTrackingIdentifier, self).setUp()
        self._uid = generate_uid()
        self._tracking_identifier = TrackingIdentifier(
            uid=self._uid
        )

    def test_uid(self):
        item = self._tracking_identifier[0]
        assert item.ConceptNameCodeSequence[0].CodeValue == '112040'
        assert item.UID == self._uid


class TestMeasurement(unittest.TestCase):

    def setUp(self):
        super(TestMeasurement, self).setUp()
        self._value = 10.0
        self._unit = codes.cid7181.SquareMillimeter
        self._tracking_identifier = TrackingIdentifier(
            uid=generate_uid(),
            identifier='prostate zone size measurement'
        )
        self._name = codes.cid7469.Area
        self._measurement = Measurement(
            name=self._name,
            value=self._value,
            unit=self._unit,
            tracking_identifier=self._tracking_identifier
        )

    def test_measurement(self):
        item = self._measurement[0]

    def test_name(self):
        item = self._measurement[0]
        assert item.ConceptNameCodeSequence[0] == self._name

    def test_value(self):
        item = self._measurement[0]
        assert len(item.MeasuredValueSequence) == 1
        assert len(item.MeasuredValueSequence[0]) == 3
        assert item.MeasuredValueSequence[0].NumericValue == DS(self._value)
        assert item.MeasuredValueSequence[0].MeasurementUnitsCodeSequence[0] == self._unit
        with pytest.raises(AttributeError):
            item.NumericValueQualifierCodeSequence

    def test_tracking_identifier(self):
        item = self._measurement[0].ContentSequence[0]
        assert item.ConceptNameCodeSequence[0].CodeValue == '112039'

    def test_tracking_unique_identifier(self):
        item = self._measurement[0].ContentSequence[1]
        assert item.ConceptNameCodeSequence[0].CodeValue == '112040'


class TestMeasurementOptional(unittest.TestCase):

    def setUp(self):
        '''Creates a Measurement for a numeric value in millimiter unit with
        derivation, method and reference to an image region.'''
        super(TestMeasurementOptional, self).setUp()
        self._value = 10
        self._unit = codes.cid7181.SquareMillimeter
        self._tracking_identifier = TrackingIdentifier(
            uid=generate_uid(),
            identifier='prostate zone size measurement'
        )
        self._derivation = codes.cid7464.Total
        self._method = codes.cid7473.AreaOfClosedIrregularPolygon
        self._location = codes.cid6300.RightAnteriorMiddlePeripheralZoneOfProstate
        self._finding_site = FindingSite(
            anatomic_location=self._location
        )
        self._image = SourceImageForRegion(
            referenced_sop_class_uid=generate_uid(),
            referenced_sop_instance_uid=generate_uid()
        )
        self._region = ImageRegion(
            graphic_type=GraphicTypes.POINT,
            graphic_data=[1.0, 1.0],
            source_image=self._image
        )
        self._name = codes.cid7469.Area
        self._measurement = Measurement(
            name=self._name,
            value=self._value,
            unit=self._unit,
            tracking_identifier=self._tracking_identifier,
            method=self._method,
            derivation=self._derivation,
            finding_sites=[self._finding_site, ],
            referenced_regions=[self._region]
        )

    def test_method(self):
        item = self._measurement[0].ContentSequence[2]
        assert item.ConceptNameCodeSequence[0].CodeValue == 'G-C036'
        assert item.ConceptCodeSequence[0] == self._method

    def test_derivation(self):
        item = self._measurement[0].ContentSequence[3]
        assert item.ConceptNameCodeSequence[0].CodeValue == '121401'
        assert item.ConceptCodeSequence[0] == self._derivation

    def test_finding_site(self):
        item = self._measurement[0].ContentSequence[4]
        assert item.ConceptNameCodeSequence[0].CodeValue == 'G-C0E3'
        assert item.ConceptCodeSequence[0] == self._location
        # Laterality and topological modifier were not specified
        assert len(item.ContentSequence) == 0


class TestROIMeasurements(unittest.TestCase):

    def setUp(self):
        super(TestROIMeasurements, self).setUp()
        self._values = [10, 20.0, 30.5]
        self._unit = codes.cid7181.SquareMillimeter
        self._tracking_identifiers = [
            TrackingIdentifier(
                uid=generate_uid(),
                identifier='{} prostate zone size measurement'.format(i)
            )
            for i in ('first', 'second', 'third')
        ]
        self._name = codes.cid7469.Area
        self._measurements = [
            Measurement(
                name=self._name,
                value=self._values[i],
                unit=self._unit,
                tracking_identifier=self._tracking_identifiers[i]
            )
            for i in range(len(self._values))
        ]
        self._method = codes.cid7473.AreaOfClosedIrregularPolygon
        self._location = codes.cid6300.RightAnteriorMiddlePeripheralZoneOfProstate
        self._finding_site = FindingSite(
            anatomic_location=self._location
        )
        self._roi_measurements = ROIMeasurements(
            measurements=self._measurements,
            method=self._method,
            finding_sites=[self._finding_site, ]
        )

    def test_constructed_with_empty_measurements(self):
        with pytest.raises(ValueError):
            ROIMeasurements(
                measurements=[],
                method=self._method,
                finding_sites=[self._finding_site, ]
            )

    def test_constructed_without_measurements(self):
        with pytest.raises(TypeError):
            ROIMeasurements(
                method=self._method,
                finding_sites=[self._finding_site, ]
            )

    def test_method(self):
        item = self._roi_measurements[0]
        assert item.ConceptNameCodeSequence[0].CodeValue == 'G-C036'
        assert item.ConceptCodeSequence[0] == self._method

    def test_finding_site(self):
        item = self._roi_measurements[1]
        assert item.ConceptNameCodeSequence[0].CodeValue == 'G-C0E3'
        assert item.ConceptCodeSequence[0] == self._location

    def test_measurement_1(self):
        item = self._roi_measurements[2]
        assert item.ConceptNameCodeSequence[0].CodeValue == 'G-A166'
        assert len(item.MeasuredValueSequence) == 1
        assert len(item.MeasuredValueSequence[0]) == 2
        subitem = item.MeasuredValueSequence[0]
        assert subitem.NumericValue == DS(self._values[0])
        assert subitem.MeasurementUnitsCodeSequence[0] == self._unit

    def test_measurement_2(self):
        item = self._roi_measurements[3]
        assert item.ConceptNameCodeSequence[0].CodeValue == 'G-A166'
        assert len(item.MeasuredValueSequence) == 1
        assert len(item.MeasuredValueSequence[0]) == 3
        subitem = item.MeasuredValueSequence[0]
        assert subitem.NumericValue == DS(self._values[1])
        assert subitem.FloatingPointValue == self._values[1]
        assert subitem.MeasurementUnitsCodeSequence[0] == self._unit

    def test_measurement_3(self):
        item = self._roi_measurements[4]
        assert item.ConceptNameCodeSequence[0].CodeValue == 'G-A166'
        assert len(item.MeasuredValueSequence) == 1
        assert len(item.MeasuredValueSequence[0]) == 3
        subitem = item.MeasuredValueSequence[0]
        assert subitem.NumericValue == DS(self._values[2])
        assert subitem.FloatingPointValue == self._values[2]
        assert subitem.MeasurementUnitsCodeSequence[0] == self._unit


class TestImageRegion(unittest.TestCase):

    def setUp(self):
        pass


class TestVolumeSurface(unittest.TestCase):

    def setUp(self):
        pass


class TestReferencedSegmentation(unittest.TestCase):

    def setUp(self):
        pass


class TestReferencedSegmentationFrame(unittest.TestCase):

    def setUp(self):
        pass


class TestPlanarROIMeasurementsAndQualitativeEvaluations(unittest.TestCase):

    def setUp(self):
        super(TestPlanarROIMeasurementsAndQualitativeEvaluations, self).setUp()
        self._tracking_identifier = TrackingIdentifier(
            uid=generate_uid(),
            identifier='planar roi measurements'
        )
        self._image = SourceImageForRegion(
            referenced_sop_class_uid=generate_uid(),
            referenced_sop_instance_uid=generate_uid()
        )
        self._region = ImageRegion(
            graphic_type=GraphicTypes.CIRCLE,
            graphic_data=[[1.0, 1.0], [2.0, 2.0]],
            source_image=self._image
        )
        self._measurements = PlanarROIMeasurementsAndQualitativeEvaluations(
            tracking_identifier=self._tracking_identifier,
            referenced_region=self._region
        )

    def test_constructed_without_human_readable_tracking_identifier(self):
        tracking_identifier = TrackingIdentifier(
            uid=generate_uid()
        )
        with pytest.raises(ValueError):
            PlanarROIMeasurementsAndQualitativeEvaluations(
                tracking_identifier=tracking_identifier,
                referenced_region=self._region
            )

    def test_constructed_without_reference(self):
        with pytest.raises(ValueError):
            PlanarROIMeasurementsAndQualitativeEvaluations(
                tracking_identifier=self._tracking_identifier
            )

    def test_constructed_with_multiple_references(self):
        with pytest.raises(ValueError):
            PlanarROIMeasurementsAndQualitativeEvaluations(
                tracking_identifier=self._tracking_identifier,
                referenced_region=self._region,
                referenced_segmentation=self._region
            )


class TestVolumetricROIMeasurementsAndQualitativeEvaluations(unittest.TestCase):

    def setUp(self):
        super(TestVolumetricROIMeasurementsAndQualitativeEvaluations, self)\
            .setUp()
        self._tracking_identifier = TrackingIdentifier(
            uid=generate_uid(),
            identifier='volumetric roi measurements'
        )
        self._images = [
            SourceImageForRegion(
                referenced_sop_class_uid=generate_uid(),
                referenced_sop_instance_uid=generate_uid()
            )
            for i in range(3)
        ]
        self._regions = [
            ImageRegion(
                graphic_type=GraphicTypes.POLYLINE,
                graphic_data=[[1.0, 1.0], [2.0, 2.0], [3.0, 3.0], [1.0, 1.0]],
                source_image=self._images[i]
            )
            for i in range(3)
        ]
        self._measurements = VolumetricROIMeasurementsAndQualitativeEvaluations(
            tracking_identifier=self._tracking_identifier,
            referenced_regions=self._regions
        )

    def test_constructed_with_volume(self):
        image = SourceImageForSegmentation(
            referenced_sop_class_uid=generate_uid(),
            referenced_sop_instance_uid=generate_uid()
        )
        volume = VolumeSurface(
            graphic_type=GraphicTypes3D.ELLIPSOID,
            graphic_data=[
                [1.0, 2.0, 2.0], [3.0, 2.0, 2.0],
                [2.0, 1.0, 2.0], [2.0, 3.0, 2.0],
                [2.0, 2.0, 1.0], [2.0, 2.0, 3.0],
            ],
            source_images=[image],
            frame_of_reference_uid=generate_uid()
        )
        measurements = VolumetricROIMeasurementsAndQualitativeEvaluations(
            tracking_identifier=self._tracking_identifier,
            referenced_volume_surface=volume
        )
        assert len(measurements) == 1
        assert len(measurements[0].ContentSequence) == 3

    def test_constructed_without_reference(self):
        with pytest.raises(ValueError):
            VolumetricROIMeasurementsAndQualitativeEvaluations(
                tracking_identifier=self._tracking_identifier
            )

    def test_constructed_with_multiple_references(self):
        with pytest.raises(ValueError):
            VolumetricROIMeasurementsAndQualitativeEvaluations(
                tracking_identifier=self._tracking_identifier,
                referenced_regions=self._regions,
                referenced_volume_surface=self._regions
            )


class TestMeasurementReport(unittest.TestCase):

    def setUp(self):
        super(TestMeasurementReport, self).setUp()
        self._observer_person_context = ObserverContext(
            observer_type=codes.cid270.Person,
            observer_identifying_attributes=PersonObserverIdentifyingAttributes(
                name='Foo Bar'
            )
        )
        self._observer_device_context = ObserverContext(
            observer_type=codes.cid270.Device,
            observer_identifying_attributes=DeviceObserverIdentifyingAttributes(
                uid=generate_uid()
            )
        )
        self._observation_context = ObservationContext(
            observer_person_context=self._observer_person_context,
            observer_device_context=self._observer_device_context
        )
        self._procedure_reported = codes.cid100.CTPerfusionHeadWithContrastIV
        self._tracking_identifier = TrackingIdentifier(
            uid=generate_uid(),
            identifier='planar roi measurements'
        )
        self._image = SourceImageForRegion(
            referenced_sop_class_uid=generate_uid(),
            referenced_sop_instance_uid=generate_uid()
        )
        self._region = ImageRegion(
            graphic_type=GraphicTypes.CIRCLE,
            graphic_data=[[1.0, 1.0], [2.0, 2.0]],
            source_image=self._image
        )
        self._measurements = PlanarROIMeasurementsAndQualitativeEvaluations(
            tracking_identifier=self._tracking_identifier,
            referenced_region=self._region
        )
        self._measurement_report = MeasurementReport(
            observation_context=self._observation_context,
            procedure_reported=self._procedure_reported,
            imaging_measurements=self._measurements
        )

    def test_container(self):
        item = self._measurement_report[0]
        assert len(item.ContentSequence) == 8
        subitem = item.ContentTemplateSequence[0]
        assert subitem.TemplateIdentifier == 'TID1500'

    def test_language(self):
        item = self._measurement_report[0].ContentSequence[0]
        assert item.ConceptNameCodeSequence[0].CodeValue == '121049'
        assert item.ConceptCodeSequence[0] == DEFAULT_LANGUAGE

    def test_observation_context(self):
        item = self._measurement_report[0].ContentSequence[1]
        assert item.ConceptNameCodeSequence[0].CodeValue == '121005'
        item = self._measurement_report[0].ContentSequence[2]
        assert item.ConceptNameCodeSequence[0].CodeValue == '121008'
        item = self._measurement_report[0].ContentSequence[3]
        assert item.ConceptNameCodeSequence[0].CodeValue == '121005'
        item = self._measurement_report[0].ContentSequence[4]
        assert item.ConceptNameCodeSequence[0].CodeValue == '121012'

    def test_procedure_reported(self):
        item = self._measurement_report[0].ContentSequence[5]
        assert item.ConceptNameCodeSequence[0].CodeValue == '121058'
        assert item.ConceptCodeSequence[0] == self._procedure_reported

    def test_image_library(self):
        item = self._measurement_report[0].ContentSequence[6]
        assert item.ConceptNameCodeSequence[0].CodeValue == '111028'

    def test_imaging_measurements(self):
        item = self._measurement_report[0].ContentSequence[7]
        assert item.ConceptNameCodeSequence[0].CodeValue == '126010'
        subitem = item.ContentSequence[0]
        assert subitem.ConceptNameCodeSequence[0].CodeValue == '125007'


class TestComprehensive3DSR(unittest.TestCase):

    def setUp(self):
        super(TestComprehensive3DSR, self).setUp()
        self._ref_dataset = Dataset()
        self._ref_dataset.PatientID = '1'
        self._ref_dataset.PatientName = 'patient'
        self._ref_dataset.SOPClassUID = generate_uid()
        self._ref_dataset.SOPInstanceUID = generate_uid()
        self._ref_dataset.SeriesInstanceUID = generate_uid()
        self._ref_dataset.StudyInstanceUID = generate_uid()
        self._ref_dataset.AccessionNumber = '2'
        self._content = Dataset()
        self._series_instance_uid = generate_uid()
        self._series_number = 3
        self._series_description = 'series'
        self._sop_instance_uid = generate_uid()
        self._instance_number = 4
        self._institution_name = 'institute'
        self._institution_department_name = 'department'
        self._manufacturer = 'manufacturer'
        self._report = Comprehensive3DSR(
            evidence=[self._ref_dataset],
            content=self._content,
            series_instance_uid=self._series_instance_uid,
            series_number=self._series_number,
            series_description=self._series_description,
            sop_instance_uid=self._sop_instance_uid,
            instance_number=self._instance_number,
            institution_name=self._institution_name,
            institution_department_name=self._institution_department_name,
            manufacturer=self._manufacturer
        )

    def test_patient_attributes(self):
        assert self._report.PatientID == self._ref_dataset.PatientID
        assert self._report.PatientName == self._ref_dataset.PatientName

    def test_study_attributes(self):
        assert self._report.StudyInstanceUID == self._ref_dataset.StudyInstanceUID
        assert self._report.AccessionNumber == self._ref_dataset.AccessionNumber

    def test_series_attributes(self):
        assert self._report.SeriesInstanceUID == self._series_instance_uid
        assert self._report.SeriesNumber == self._series_number
        assert self._report.SeriesDescription == self._series_description

    def test_instance_attributes(self):
        assert self._report.SOPInstanceUID == self._sop_instance_uid
        assert self._report.InstanceNumber == self._instance_number
        assert self._report.SOPClassUID == '1.2.840.10008.5.1.4.1.1.88.34'
        assert self._report.InstitutionName == self._institution_name
        assert self._report.Manufacturer == self._manufacturer
        assert self._report.Modality == 'SR'
