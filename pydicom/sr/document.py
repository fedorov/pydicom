import collections
import datetime

from pydicom.dataset import Dataset
from pydicom.uid import PYDICOM_IMPLEMENTATION_UID, ExplicitVRLittleEndian
from pydicom.valuerep import DA, DT, TM
from pydicom._storage_sopclass_uids import Comprehensive3DSRStorage


_ATTRIBUTES_TO_INCLUDE = {
    # Patient
    '00080054', '00080100', '00080102', '00080103', '00080104', '00080105',
    '00080106', '00080107', '0008010B', '0008010D', '0008010F', '00080117',
    '00080118', '00080119', '00080120', '00080121', '00080122', '00081120',
    '00081150', '00081155', '00081160', '00081190', '00081199', '00100010',
    '00100020', '00100021', '00100022', '00100024', '00100026', '00100027',
    '00100028', '00100030', '00100032', '00100033', '00100034', '00100035',
    '00100040', '00100200', '00100212', '00100213', '00100214', '00100215',
    '00100216', '00100217', '00100218', '00100219', '00100221', '00100222',
    '00100223', '00100229', '00101001', '00101002', '00101100', '00102160',
    '00102201', '00102202', '00102292', '00102293', '00102294', '00102295',
    '00102296', '00102297', '00102298', '00102299', '00104000', '00120062',
    '00120063', '00120064', '0020000D', '00400031', '00400032', '00400033',
    '00400035', '00400036', '00400039', '0040003A', '0040E001', '0040E010',
    '0040E020', '0040E021', '0040E022', '0040E023', '0040E024', '0040E025',
    '0040E030', '0040E031', '0062000B', '00880130', '00880140',
    # Patient Study
    '00080100', '00080102', '00080103', '00080104', '00080105', '00080106',
    '00080107', '0008010B', '0008010D', '0008010F', '00080117', '00080118',
    '00080119', '00080120', '00080121', '00080122', '00081080', '00081084',
    '00101010', '00101020', '00101021', '00101022', '00101023', '00101024',
    '00101030', '00102000', '00102110', '00102180', '001021A0', '001021B0',
    '001021C0', '001021D0', '00102203', '00380010', '00380014', '00380060',
    '00380062', '00380064', '00380500', '00400031', '00400032', '00400033',
    # General Study
    '00080020', '00080030', '00080050', '00080051', '00080080', '00080081',
    '00080082', '00080090', '00080096', '0008009C', '0008009D', '00080100',
    '00080102', '00080103', '00080104', '00080105', '00080106', '00080107',
    '0008010B', '0008010D', '0008010F', '00080117', '00080118', '00080119',
    '00080120', '00080121', '00080122', '00081030', '00081032', '00081048',
    '00081049', '00081060', '00081062', '00081110', '00081150', '00081155',
    '0020000D', '00200010', '00321034', '00400031', '00400032', '00400033',
    '00401012', '00401101', '00401102', '00401103', '00401104',
    # Clinical Trial Subject
    '00120010', '00120020', '00120021', '00120030', '00120031', '00120040',
    '00120042', '00120081', '00120082',
    # Clinical Trial Study
    '00120020', '00120050', '00120051', '00120052', '00120053', '00120083',
    '00120084', '00120085',
}


class Comprehensive3DSR(Dataset):

    '''Comprehensive 3D Structured Report (SR), whose content may include
    textual and a variety of coded information, numeric measurement values,
    references to the SOP Instances and 2D or 3D spatial or temporal regions of
    interest within such SOP Instances.
    '''

    def __init__(self, evidence, content,
                 series_instance_uid, series_number, series_description,
                 sop_instance_uid, instance_number,
                 institution_name, institution_department_name, manufacturer,
                 is_complete=False, is_final=False, is_verified=False,
                 verifying_observer_name=None, verifying_organization=None,
                 performed_procedure_codes=None, requested_procedures=None):
        '''
        Parameters
        ----------
        evidence: List[pydicom.dataset.Dataset]
            instances, which are referenced in the content tree and from which
            the created SR document instance should inherit patient and study
            information
        content: pydicom.dataset.Dataset
            root container content items that should be included in the
            SR document
        series_instance_uid: str
            Series Instance UID of the SR document series
        series_number: Union[int, None]
            Series Number of the SR document series
        series_description: str
            Series Description of the SR document series
            (may be freetext or a code sequence)
        sop_instance_uid: str
            SOP instance UID that should be assigned to the SR document instance
        instance_number: int
            number that should be assigned to this SR document instance
        institution_name: str
            name of the institution of the person or device that creates the
            SR document instance
        institution_department_name: str
            name of the department of the person or device that creates the
            SR document instance
        manufacturer: str
            name of the manufacturer of the device that creates the SR document
            instance (in a research setting this is typically the same
            as `institution_name`)
        is_complete: bool, optional
            whether the content is complete (default: ``False``)
        is_final: bool, optional
            whether the report is the definitive means of communicating the
            findings (default: ``False``)
        is_verified: bool, optional
            whether the report has been verified by an observer accountable
            for its content (default: ``False``)
        verifying_observer_name: Union[str, None], optional
            name of the person that verfied the SR document
            (required if `is_verified`)
        verifying_organization: str
            name of the organization that verfied the SR document
            (required if `is_verified`)
        performed_procedure_codes: List[pydicom.sr.value_types.CodedConcept]
            codes of the performed procedures that resulted in the SR document
        requested_procedures: List[pydicom.dataset.Dataset]
            requested procedures that are being fullfilled by creation of the
            SR document

        '''
        super(Comprehensive3DSR, self).__init__()
        self.SOPClassUID = Comprehensive3DSRStorage
        self.SOPInstanceUID = str(sop_instance_uid)

        self.is_implicit_VR = False
        self.is_little_endian = True
        self.preamble = b'\x00' * 128
        self.file_meta = Dataset()
        self.file_meta.MediaStorageSOPClassUID = self.SOPClassUID
        self.file_meta.MediaStorageSOPInstanceUID = self.SOPInstanceUID
        self.file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
        self.file_meta.ImplementationClassUID = PYDICOM_IMPLEMENTATION_UID
        self.file_meta.FileMetaInformationGroupLength = 0
        self.file_meta.FileMetaInformationVersion = b'\x00\x01'

        self.Modality = 'SR'
        self.SeriesDescription = str(series_description)
        self.SeriesInstanceUID = str(series_instance_uid)
        self.SeriesNumber = series_number
        self.InstanceNumber = instance_number

        self.InstitutionName = institution_name
        self.InstitutionalDepartmentName = institution_department_name
        self.Manufacturer = manufacturer

        now = datetime.datetime.now()
        if is_complete:
            self.CompletionFlag = 'COMPLETE'
        else:
            self.CompletionFlag = 'PARTIAL'
        if is_verified:
            if verifying_observer_name is None:
                raise ValueError(
                    'Verifying Observer Name must be specified if SR document '
                    'has been verified.'
                )
            if verifying_organization is None:
                raise ValueError(
                    'Verifying Organization must be specified if SR document '
                    'has been verified.'
                )
            self.VerificationFlag = 'VERIFIED'
            ovserver_item = Dataset()
            ovserver_item.VerifyingObserverName = verifying_observer_name
            ovserver_item.VerifyingOrganization = verifying_organization
            ovserver_item.VerificationDateTime = DT(now)
            self.VerifyingObserverSequence = [observer_item]
        else:
            self.VerificationFlag = 'UNVERIFIED'
        if is_final:
            self.PreliminaryFlag = 'FINAL'
        else:
            self.PreliminaryFlag = 'PRELIMINARY'

        self.ContentDate = DA(now.date())
        self.ContentTime = TM(now.time())
        # Add content
        for tag, value in content.items():
            self[tag] = value

        ref_series_collection = collections.defaultdict(list)
        for ref in evidence:
            if ref.StudyInstanceUID != evidence[0].StudyInstanceUID:
                raise ValueError(
                    'Referenced data sets must all belong to the same study.'
                )
            ref_instance_item = Dataset()
            ref_instance_item.ReferencedSOPClassUID = ref.SOPClassUID
            ref_instance_item.ReferencedSOPInstanceUID = ref.SOPInstanceUID
            ref_series_collection[ref.SeriesInstanceUID].append(
                ref_instance_item
            )
        ref_study_item = Dataset()
        ref_study_item.StudyInstanceUID = evidence[0].StudyInstanceUID
        ref_study_item.ReferencedSeriesSequence = []
        for ref_series_uid, ref_instance_items in ref_series_collection.items():
            ref_series_item = Dataset()
            ref_series_item.SeriesInstanceUID = ref_series_uid
            ref_series_item.ReferencedSOPSequence = ref_instance_items
            ref_study_item.ReferencedSeriesSequence.append(ref_series_item)
        if requested_procedures is not None:
            self.ReferencedRequestSequence = requested_procedures
            self.CurrentRequestedProcedureEvidenceSequence = [ref_study_item]
        else:
            self.PertinentOtherEvidenceSequence = [ref_study_item]

        if performed_procedure_codes is not None:
            self.PerformedProcedureCodeSequence = performed_procedure_codes
        else:
            self.PerformedProcedureCodeSequence = []

        # TODO
        self.ReferencedPerformedProcedureStepSequence = []

        # Copy all patient and study level attributes from one of the
        # referenced data sets.
        for tag in _ATTRIBUTES_TO_INCLUDE:
            try:
                data_element = evidence[0][tag]
            except KeyError:
                continue
            self.add(data_element)
