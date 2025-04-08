Brain Imaging Data Structure Specification

#### ᴠ1.8.

#### 2022-10-


## Contents



















- The Brain Imaging Data Structure
- Introduction
   - Motivation
   - Extensions
   - Citing BIDS
      - Original publication
      - Datatype specific publications.
      - Research Resource Identifier (RRID)
- Common principles
   - Definitions
   - Entities
   - Compulsory, optional, and additional data and metadata
   - Filesystem structure
      - Other top level directories
   - Filenames.
      - Entity-linked file collections.
      - Case collision intolerance
   - Source vs. raw vs. derived data
      - Storage of derived datasets
      - Non-compliant derivatives
   - File Formation specification.
      - Imaging files
      - Tabular files
      - Key-value files (dictionaries)
   - The Inheritance Principle
   - Participant names and other labels.
   - Specification of paths
   - Uniform Resource Indicator.
      - BIDS URI
   - Units.
   - Directory structure.
      - Single session example.
   - Unspecified data
- Modality agnostic files
   - Dataset description.
      - dataset_description.json
      - README.
      - CHANGES.
      - LICENSE.
   - Participants file.
   - Samples file
   - Phenotypic and assessment data
   - Scans file
   - Sessions file
   - Code.
- Magnetic Resonance Imaging
   - Common metadata fields
      - Scanner Hardware
      - Sequence Specifics
      - In-Plane Spatial Encoding.
      - Timing Parameters.
      - RF & Contrast
      - Slice Acceleration.
      - Anatomical landmarks.
      - Echo-Planar Imaging and B0 mapping.
      - Institution information
   - Anatomy imaging data
      - Deprecated suffixes.
   - Task (including resting state) imaging data
      - Required fields
      - Other RECOMMENDED metadata
   - Diffusion imaging data.
      - REQUIRED gradient orientation information.
      - Multipart (split) DWI schemes
      - Other RECOMMENDED metadata
   - Arterial Spin Labeling perfusion data
      - *_aslcontext.tsv.
      - Scaling.
      - M0.
      - *_asl.jsonfile.
      - m0scanmetadata fields
   - Fieldmap data
      - Expressing the MR protocol intent for fieldmaps
      - Types of fieldmaps.
- Magnetoencephalography
   - MEG recording data
      - Recording EEG simultaneously with MEG.
      - Sidecar JSON (*_meg.json)
   - Channels description (*_channels.tsv)
      - Example*_channels.tsv.
   - Coordinate System JSON (*_coordsystem.json)
   - Landmark photos (*_photo.jpg).
      - Example*_photo.jpg.
   - Head shape and electrode description (*_headshape.<ext>).
   - Empty-room MEG recordings.
      - Example 1.
      - Example 2.
- Electroencephalography
   - EEG recording data
      - Sidecar JSON (*_eeg.json)
   - Channels description (*_channels.tsv)
      - Example*_channels.tsv.
   - Electrodes description (*_electrodes.tsv)
      - Example*_electrodes.tsv
   - Coordinate System JSON (*_coordsystem.json)
      - Example*_coordsystem.json
   - Landmark photos (*_photo.jpg).
      - Example*_photo.jpg.
- Intracranial Electroencephalography
   - iEEG recording data
      - Terminology: Electrodes vs. Channels
      - Sidecar JSON (*_ieeg.json)
   - Channels description (*_channels.tsv)
      - Example*_channels.tsv.
   - Electrode description (*_electrodes.tsv).
      - Example*_electrodes.tsv
   - Coordinate System JSON (*_coordsystem.json)
      - Recommended 3D coordinate systems
      - Allowed 2D coordinate systems
      - Multiple coordinate systems.
      - Example*_coordsystem.json
   - Photos of the electrode positions (*_photo.jpg).
      - Example*_photo.jpg.
   - Electrical stimulation
      - Example*_events.tsv
- Task events
   - Stimuli
      - Stimuli directory
      - Stimuli databases.
      - Stimulus presentation details
- Physiological and other continuous recordings
   - Recommendations for specific use cases
- Behavioral experiments (with no neural recordings)
   - RECOMMENDED metadata
- Genetic Descriptor
   - Dataset Description
   - Subject naming and Participants file
   - Genetic Information
- Positron Emission Tomography
   - Terminology and conventions.
   - PET recording data
      - Shared MRI data along with PET.
      - PET metadata
      - Recommended patient data.
   - Blood recording data.
      - Example blood data
- Microscopy
   - Microscopy imaging data
      - File formats.
      - Modality suffixes.
      - Filename entities.
      - Microscopy metadata (Sidecar JSON).
   - Required Samples file
   - Recommended Participants data
   - Photos of the samples (*_photo.<extension>)
- Near-Infrared Spectroscopy
   - NIRS recording data
      - Terminology
      - Sidecar JSON (*_nirs.json)
   - Channels description (*_channels.tsv)
      - Restricted keyword list for the channel types
      - Example*_channels.tsv.
   - Optode description (*_optodes.tsv)
      - Example*_optodes.tsv
   - Coordinate System JSON (*_coordsystem.json)
      - Example*_coordsystem.json
- BIDS Derivatives
   - Metadata conventions
   - File naming conventions.
- Common data types and metadata
   - Common file level metadata fields
      - Examples
   - Spatial references.
      - SpatialReference key allowed values
      - Examples
   - Preprocessed or cleaned data
- Imaging data types
   - Preprocessed, coregistered and/or resampled volumes.
   - Masks
   - Segmentations
      - Discrete Segmentations
      - Probabilistic Segmentations.
      - Discrete surface segmentations
      - Common image-derived labels
- Longitudinal and multi-site studies
   - Multi-site or multi-center studies.
      - Option 1: Treat each site/center as a separate dataset.
      - Option 2: Combining sites/centers into one dataset
- Glossary of schema objects
   - ACCELChannelCount (metadata)
   - Acknowledgements (metadata)
   - AcquisitionDuration (metadata)
   - AcquisitionMode (metadata)
   - AcquisitionVoxelSize (metadata)
   - Anaesthesia (metadata)
   - AnalyticalApproach (metadata)
   - AnatomicalLandmarkCoordinateSystem (metadata)
   - AnatomicalLandmarkCoordinateSystemDescription (metadata).
   - AnatomicalLandmarkCoordinateUnits (metadata)
   - AnatomicalLandmarkCoordinates sense 1 (metadata)
   - AnatomicalLandmarkCoordinates sense 2 (metadata)
   - Any (extensions)
   - ArterialSpinLabelingType (metadata)
   - AssociatedEmptyRoom (metadata).
   - Atlas (metadata)
   - AttenuationCorrection (metadata)
   - AttenuationCorrectionMethodReference (metadata)
   - Authors (metadata)
   - B0FieldIdentifier (metadata)
   - B0FieldSource (metadata)
   - BF (suffixes).
   - BIDSVersion (metadata).
   - BackgroundSuppression (metadata)
   - BackgroundSuppressionNumberPulses (metadata)
   - BackgroundSuppressionPulseTime (metadata)
   - BasedOn (metadata).
   - BloodDensity (metadata)
   - BodyPart (metadata)
   - BodyPartDetails (metadata).
   - BodyPartDetailsOntology (metadata)
   - BolusCutOffDelayTime (metadata).
   - BolusCutOffFlag (metadata)
   - BolusCutOffTechnique (metadata)
   - BrainLocation (metadata)
- CARS (suffixes).
- CASLType (metadata).
- CHANGES (files)
- CONF (suffixes).
- CTF (extensions)
- CapManufacturer (metadata).
- CapManufacturersModelName (metadata)
- CellType (metadata).
- Chimap (suffixes).
- ChunkTransformationMatrix (metadata)
- ChunkTransformationMatrixAxis (metadata).
- Code (metadata)
- CogAtlasID (metadata)
- CogPOID (metadata).
- CoilCombinationMethod (metadata)
- Columns (metadata).
- ContinuousHeadLocalization (metadata).
- ContrastBolusIngredient (metadata)
- DCOffsetCorrection (metadata).
- DF (suffixes)
- DIC (suffixes)
- DatasetDOI (metadata)
- DatasetLinks (metadata)
- DatasetType (metadata).
- DecayCorrectionFactor (metadata).
- DelayAfterTrigger (metadata)
- DelayTime (metadata).
- Density (metadata).
- Derivative (metadata)
- Description (metadata)
- DetectorType (metadata)
- DeviceSerialNumber (metadata)
- DewarPosition (metadata).
- DigitizedHeadPoints sense 1 (metadata)
- DigitizedHeadPoints sense 2 (metadata)
- DigitizedHeadPointsCoordinateSystem (metadata)
- DigitizedHeadPointsCoordinateSystemDescription (metadata).
- DigitizedHeadPointsCoordinateUnits (metadata)
- DigitizedLandmarks (metadata)
- Directory (extensions)
- DispersionConstant (metadata)
- DispersionCorrected (metadata)
- DoseCalibrationFactor (metadata)
- DwellTime (metadata).
- ECGChannelCount (metadata)
- ECOGChannelCount (metadata)
- EEGChannelCount (metadata)
- EEGCoordinateSystem (metadata)
- EEGCoordinateSystemDescription (metadata)
- EEGCoordinateUnits (metadata)
- EEGGround (metadata)
- EEGPlacementScheme (metadata)
- EEGReference (metadata).
- EMGChannelCount (metadata).
- EOGChannelCount (metadata)
- EchoTime sense 1 (metadata)
- EchoTime sense 2 (metadata)
- EchoTime1 (metadata)
- EchoTime2 (metadata)
- EffectiveEchoSpacing (metadata).
- ElectricalStimulation (metadata).
- ElectricalStimulationParameters (metadata)
- ElectrodeManufacturer (metadata).
- ElectrodeManufacturersModelName (metadata)
- EpochLength (metadata)
- EstimationAlgorithm (metadata).
- EstimationReference (metadata)
- EthicsApprovals (metadata).
- FLAIR (suffixes)
- FLASH (suffixes)
- FLUO (suffixes).
- FiducialsCoordinateSystem (metadata)
- FiducialsCoordinateSystemDescription (metadata)
- FiducialsCoordinateUnits (metadata)
- FiducialsCoordinates (metadata)
- FiducialsDescription (metadata)
- FlipAngle (metadata)
- FrameDuration (metadata)
- FrameTimesStart (metadata)
- Funding (metadata)
- GYROChannelCount (metadata)
- GeneratedBy (metadata)
- GeneticLevel (metadata).
- Genetics (metadata)
- GradientSetType (metadata)
- HED (columns)
- HED (metadata)
- HEDVersion (metadata)
- Haematocrit (metadata).
- HardcopyDeviceSoftwareVersion (metadata)
- HardwareFilters (metadata).
- HeadCircumference (metadata).
- HeadCoilCoordinateSystem (metadata)
- HeadCoilCoordinateSystemDescription (metadata)
- HeadCoilCoordinateUnits (metadata)
- HeadCoilCoordinates (metadata)
- HeadCoilFrequency (metadata).
- HowToAcknowledge (metadata)
- IRT1 (suffixes)
- ImageAcquisitionProtocol (metadata)
- ImageDecayCorrected (metadata)
- ImageDecayCorrectionTime (metadata)
- Immersion (metadata).
- InfusionRadioactivity (metadata)
- InfusionSpeed (metadata)
- InfusionSpeedUnits (metadata)
- InfusionStart (metadata)
- InjectedMass (metadata).
- InjectedMassPerWeight (metadata)
- InjectedMassPerWeightUnits (metadata)
- InjectedMassUnits (metadata).
- InjectedRadioactivity (metadata).
- InjectedRadioactivityUnits (metadata).
- InjectedVolume (metadata).
- InjectionEnd (metadata).
- InjectionStart (metadata)
- InstitutionAddress (metadata)
- InstitutionName (metadata).
- InstitutionalDepartmentName (metadata).
- Instructions (metadata)
- IntendedFor sense 1 (metadata).
- IntendedFor sense 2 (metadata).
- InversionTime (metadata).
- LICENSE (files).
- LabelingDistance (metadata)
- LabelingDuration (metadata)
- LabelingEfficiency (metadata)
- LabelingLocationDescription (metadata).
- LabelingOrientation (metadata)
- LabelingPulseAverageB1 (metadata).
- LabelingPulseAverageGradient (metadata)
- LabelingPulseDuration (metadata).
- LabelingPulseFlipAngle (metadata)
- LabelingPulseInterval (metadata)
- LabelingPulseMaximumGradient (metadata)
- LabelingSlabThickness (metadata)
- Levels (metadata)
- License (metadata).
- LongName (metadata).
- LookLocker (metadata)
- M0Estimate (metadata)
- M0Type (metadata)
- M0map (suffixes).
- MAGNChannelCount (metadata).
- MEGChannelCount (metadata).
- MEGCoordinateSystem (metadata).
- MEGCoordinateSystemDescription (metadata)
- MEGCoordinateUnits (metadata).
- MEGRE (suffixes)
- MEGREFChannelCount (metadata)
- MESE (suffixes).
- MP2RAGE (suffixes).
- MPE (suffixes)
- MPM (suffixes)
- MRAcquisitionType (metadata)
- MRTransmitCoilSequence (metadata)
- MTNumberOfPulses (metadata)
- MTOffsetFrequency (metadata)
- MTPulseBandwidth (metadata).
- MTPulseDuration (metadata).
- MTPulseShape (metadata)
- MTR (suffixes)
- MTRmap (suffixes).
- MTS (suffixes)
- MTState (metadata)
- MTVmap (suffixes).
- MTsat (suffixes)
- MWFmap (suffixes)
- MagneticFieldStrength (metadata)
- Magnification (metadata)
- Manual (metadata).
- Manufacturer (metadata)
- ManufacturersModelName (metadata).
- MatrixCoilMode (metadata).
- MaxMovement (metadata)
- MeasurementToolMetadata (metadata)
- MetaboliteAvail (metadata).
- MetaboliteMethod (metadata)
- MetaboliteRecoveryCorrectionApplied (metadata)
- MiscChannelCount (metadata)
- MixingTime (metadata)
- ModeOfAdministration (metadata).
- MolarActivity (metadata)
- MolarActivityMeasTime (metadata)
- MolarActivityUnits (metadata)
- MultibandAccelerationFactor (metadata)
- MultipartID (metadata)
- NIRSChannelCount (metadata).
- NIRSCoordinateProcessingDescription (metadata)
- NIRSCoordinateSystem (metadata).
- NIRSCoordinateSystemDescription (metadata)
- NIRSCoordinateUnits (metadata).
- NIRSDetectorOptodeCount (metadata)
- NIRSPlacementScheme (metadata).
- NIRSSourceOptodeCount (metadata).
- NLO (suffixes).
- Name (metadata).
- NegativeContrast (metadata)
- None (extensions)
- NonlinearGradientCorrection (metadata)
- NumberOfVolumesDiscardedByScanner (metadata)
- NumberOfVolumesDiscardedByUser (metadata)
- NumberShots (metadata)
- NumericalAperture (metadata)
- OCT (suffixes).
- OMEBigTiff (extensions).
- OMETiff (extensions)
- OMEZARR (extensions)
- OperatingSystem (metadata)
- OtherAcquisitionParameters (metadata).
- PASLType (metadata).
- PC (suffixes)
- PCASLType (metadata)
- PD (suffixes)
- PDT2 (suffixes).
- PDT2map (suffixes)
- PDmap (suffixes)
- PDw (suffixes)
- PLI (suffixes)
- ParallelAcquisitionTechnique (metadata)
- ParallelReductionFactorInPlane (metadata).
- PartialFourier (metadata)
- PartialFourierDirection (metadata).
- PharmaceuticalDoseAmount (metadata).
- PharmaceuticalDoseRegimen (metadata)
- PharmaceuticalDoseTime (metadata)
- PharmaceuticalDoseUnits (metadata)
- PharmaceuticalName (metadata).
- PhaseEncodingDirection (metadata)
- PhotoDescription (metadata)
- PixelSize (metadata).
- PixelSizeUnits (metadata)
- PlasmaAvail (metadata).
- PlasmaFreeFraction (metadata)
- PlasmaFreeFractionMethod (metadata)
- PostLabelingDelay (metadata)
- PowerLineFrequency (metadata).
- PromptRate (metadata)
- PulseSequenceDetails (metadata).
- PulseSequenceType (metadata).
- Purity (metadata)
- R1map (suffixes)
- R2map (suffixes)
- R2starmap (suffixes).
- RB1COR (suffixes)
- RB1map (suffixes)
- README (files).
- RandomRate (metadata)
- RawSources (metadata)
- ReceiveCoilActiveElements (metadata)
- ReceiveCoilName (metadata)
- ReconFilterSize (metadata)
- ReconFilterType (metadata)
- ReconMethodImplementationVersion (metadata).
- ReconMethodName (metadata).
- ReconMethodParameterLabels (metadata)
- ReconMethodParameterUnits (metadata)
- ReconMethodParameterValues (metadata)
- RecordingDuration (metadata)
- RecordingType (metadata)
- ReferencesAndLinks (metadata)
- RepetitionTime (metadata)
- RepetitionTimeExcitation (metadata)
- RepetitionTimePreparation (metadata)
- Resolution (metadata).
- S0map (suffixes)
- SEEGChannelCount (metadata)
- SEM (suffixes).
- SPIM (suffixes)
- SR (suffixes).
- SampleEmbedding (metadata)
- SampleEnvironment (metadata)
- SampleExtractionInstitution (metadata).
- SampleExtractionProtocol (metadata).
- SampleFixation (metadata)
- SampleOrigin (metadata)
- SamplePrimaryAntibody (metadata).
- SampleSecondaryAntibody (metadata).
- SampleStaining (metadata)
- SamplingFrequency sense 1 (metadata)
- SamplingFrequency sense 2 (metadata)
- ScaleFactor (metadata)
- ScanDate (metadata).
- ScanOptions (metadata)
- ScanStart (metadata)
- ScanningSequence (metadata).
- ScatterFraction (metadata)
- SequenceName (metadata)
- SequenceVariant (metadata)
- ShortChannelCount (metadata).
- SinglesRate (metadata)
- SkullStripped (metadata)
- SliceEncodingDirection (metadata).
- SliceThickness (metadata).
- SliceTiming (metadata)
- SoftwareFilters (metadata)
- SoftwareName (metadata).
- SoftwareRRID (metadata).
- SoftwareVersion (metadata)
- SoftwareVersions (metadata)
- SourceDatasets (metadata)
- SourceType (metadata)
- Sources (metadata).
- SpatialReference (metadata)
- SpecificRadioactivity (metadata)
- SpecificRadioactivityMeasTime (metadata)
- SpecificRadioactivityUnits (metadata).
- SpoilingGradientDuration (metadata)
- SpoilingGradientMoment (metadata).
- SpoilingRFPhaseIncrement (metadata)
- SpoilingState (metadata).
- SpoilingType (metadata)
- StartTime (metadata)
- StationName (metadata).
- StimulusPresentation (metadata).
- SubjectArtefactDescription (metadata).
- T1map (suffixes)
- T1rho (suffixes).
- T1w (suffixes).
- T2map (suffixes)
- T2star (suffixes)
- T2starmap (suffixes).
- T2starw (suffixes)
- T2w (suffixes).
- TB1AFI (suffixes).
- TB1DAM (suffixes).
- TB1EPI (suffixes).
- TB1RFM (suffixes)
- TB1SRGE (suffixes)
- TB1TFL (suffixes)
- TB1map (suffixes)
- TEM (suffixes)
- TaskDescription (metadata).
- TaskName (metadata).
- TermURL (metadata)
- TimeZero (metadata)
- TissueDeformationScaling (metadata)
- TissueOrigin (metadata).
- TotalAcquiredPairs (metadata).
- TotalReadoutTime (metadata)
- TracerMolecularWeight (metadata)
- TracerMolecularWeightUnits (metadata)
- TracerName (metadata).
- TracerRadLex (metadata).
- TracerRadionuclide (metadata).
- TracerSNOMED (metadata).
- TriggerChannelCount (metadata)
- TubingLength (metadata).
- TubingType (metadata).
- TwoPE (suffixes)
- Type (metadata)
- UNIT1 (suffixes)
- Units (metadata)
- VFA (suffixes)
- VascularCrushing (metadata).
- VascularCrushingVENC (metadata)
- VolumeTiming (metadata)
- WholeBloodAvail (metadata)
- WithdrawalRate (metadata)
- abbreviation (columns)
- acq_time sense 1 (columns)
- acq_time sense 2 (columns)
- acquisition (entities)
- age (columns).
- anat (datatypes)
- angio (suffixes)
- asl (suffixes).
- aslcontext (suffixes)
- asllabeling (suffixes)
- atlas (entities).
- ave (extensions)
- bdf (extensions)
- beh (datatypes).
- beh (modalities)
- beh (suffixes)
- bids_uri (formats)
- blood (suffixes)
- bold (suffixes).
- boolean (formats)
- bval (extensions)
- bvec (extensions).
- cardiac (columns).
- cbv (suffixes)
- ceagent (entities)
- channels (suffixes)
- chn (extensions)
- chunk (entities).
- code (files).
- color (columns).
- con (extensions)
- coordsystem (suffixes)
- dat (extensions).
- data_acquisition (common_principles).
- data_type (common_principles).
- dataset (common_principles)
- dataset_description (files)
- dataset_relative (formats).
- date (formats)
- datetime (formats)
- defacemask (suffixes)
- density (entities)
- deprecated (common_principles)
- derivatives (files)
- derived_from (columns)
- description (entities)
- description sense 1 (columns)
- description sense 2 (columns)
- detector sense 1 (columns).
- detector_type (columns).
- dimension (columns).
- direction (entities)
- dlabelnii (extensions).
- dseg (suffixes).
- duration (columns).
- dwi (datatypes).
- dwi (suffixes)
- echo (entities).
- edf (extensions).
- eeg (datatypes).
- eeg (extensions).
- eeg (modalities).
- eeg (suffixes)
- electrodes (suffixes).
- epi (suffixes)
- event (common_principles)
- events (suffixes).
- extension (common_principles)
- fdt (extensions).
- fieldmap (suffixes)
- fif (extensions)
- file_relative (formats)
- filename (columns).
- flip (entities)
- fmap (datatypes).
- func (datatypes)
- genetic_info (files)
- group sense 1 (columns)
- handedness (columns)
- headshape (suffixes)
- hed_version (formats)
- hemisphere (columns)
- hemisphere (entities).
- high_cutoff (columns)
- hplc_recovery_fractions (columns)
- iEEGCoordinateProcessingDescription (metadata)
- iEEGCoordinateProcessingReference (metadata)
- iEEGCoordinateSystem (metadata).
- iEEGCoordinateSystemDescription (metadata)
- iEEGCoordinateUnits (metadata).
- iEEGElectrodeGroups (metadata)
- iEEGGround (metadata).
- iEEGPlacementScheme (metadata).
- iEEGReference (metadata)
- ieeg (datatypes).
- ieeg (modalities)
- ieeg (suffixes)
- impedance (columns).
- index (columns)
- index (common_principles)
- index (formats).
- inplaneT1 (suffixes)
- inplaneT2 (suffixes)
- integer (formats)
- inversion (entities)
- jpg (extensions).
- json (extensions)
- kdf (extensions)
- label (common_principles).
- label (entities).
- label (formats)
- labelgii (extensions)
- low_cutoff (columns).
- m0scan (suffixes).
- magnitude (suffixes)
- magnitude1 (suffixes)
- magnitude2 (suffixes)
- manufacturer (columns).
- mapping (columns).
- markers (suffixes).
- mask (suffixes)
- material (columns)
- md (extensions).
- mefd (extensions)
- meg (datatypes)
- meg (modalities)
- meg (suffixes).
- metabolite_parent_fraction (columns)
- metabolite_polar_fraction (columns).
- mhd (extensions).
- micr (datatypes)
- micr (modalities)
- modality (common_principles)
- modality (entities)
- mri (modalities).
- mrk (extensions)
- mtransfer (entities).
- name sense 1 (columns)
- name sense 2 (columns)
- name sense 3 (columns)
- name sense 4 (columns)
- nii (extensions)
- niigz (extensions).
- nirs (datatypes).
- nirs (modalities)
- nirs (suffixes)
- notch (columns)
- number (formats)
- nwb (extensions)
- onset (columns).
- optodes (suffixes).
- orientation_component (columns)
- part (entities)
- participant_id (columns).
- participant_relative (formats).
- participants (files)
- pathology (columns).
- perf (datatypes)
- pet (datatypes)
- pet (modalities).
- pet (suffixes)


phase (suffixes).................................................................................. 429
phase1 (suffixes)................................................................................. 430
phase2 (suffixes)................................................................................. 430
phasediff (suffixes)................................................................................ 430
photo (suffixes).................................................................................. 430
physio (suffixes)................................................................................. 430
plasma_radioactivity (columns)......................................................................... 431
png (extensions)................................................................................. 431
pos (extensions).................................................................................. 431
probseg (suffixes)................................................................................. 431
processing (entities)............................................................................... 432
raw (extensions)................................................................................. 432
reconstruction (entities)............................................................................. 432
recording (entities)................................................................................ 433
reference sense 1 (columns)........................................................................... 433
reference sense 2 (columns)........................................................................... 433
resolution (entities)................................................................................ 434
respiratory (columns).............................................................................. 434
response_time (columns)............................................................................. 434
rrid (formats)................................................................................... 435
rst (extensions).................................................................................. 435
run (common_principles)............................................................................ 435
run (entities)................................................................................... 435
sample (columns)................................................................................. 436
sample (common_principles).......................................................................... 436
sample (entities)................................................................................. 436
sample_id (columns)............................................................................... 436
sample_type (columns)............................................................................. 437
samples (files)................................................................................... 437
sampling_frequency (columns)......................................................................... 438
sbref (suffixes).................................................................................. 438
scans (suffixes).................................................................................. 438
session (common_principles).......................................................................... 438
session (entities)................................................................................. 439
session_id (columns)............................................................................... 439
sessions (suffixes)................................................................................. 439
set (extensions).................................................................................. 440
sex (columns)................................................................................... 440
short_channel (columns)............................................................................. 440
size (columns)................................................................................... 441


snirf (extensions)................................................................................. 441
software_filters (columns)............................................................................ 441
source sense 1 (columns)............................................................................. 441
source sense 2 (columns)............................................................................. 442
sourcedata (files)................................................................................. 442
space (entities).................................................................................. 442
species (columns)................................................................................. 443
split (entities)................................................................................... 443
sqd (extensions)................................................................................. 443
stain (entities).................................................................................. 444
status (columns)................................................................................. 444
status_description (columns).......................................................................... 444
stim (suffixes)................................................................................... 445
stim_file (columns)................................................................................ 445
stimuli (files)................................................................................... 445
stimuli_relative (formats)............................................................................ 446
strain (columns)................................................................................. 446
strain_rrid (columns)............................................................................... 446
string (formats).................................................................................. 446
subject (common_principles).......................................................................... 447
subject (entities)................................................................................. 447
suffix (common_principles)........................................................................... 447
task (common_principles)............................................................................ 447
task (entities)................................................................................... 448
template_x (columns).............................................................................. 448
template_y (columns).............................................................................. 448
template_z (columns).............................................................................. 449
tif (extensions).................................................................................. 449
time (columns).................................................................................. 449
time (formats).................................................................................. 450
tracer (entities).................................................................................. 450
trg (extensions).................................................................................. 450
trial_type (columns)............................................................................... 450
trigger (columns)................................................................................. 451
tsv (extensions).................................................................................. 451
tsvgz (extensions)................................................................................ 451
txt (extensions).................................................................................. 451
type sense 1 (columns).............................................................................. 452
type sense 2 (columns).............................................................................. 452
type sense 3 (columns).............................................................................. 452


```
type sense 4 (columns).............................................................................. 453
type sense 5 (columns).............................................................................. 453
type sense 6 (columns).............................................................................. 453
uCT (suffixes)................................................................................... 453
unit (formats)................................................................................... 454
units sense 1 (columns).............................................................................. 454
units sense 2 (columns).............................................................................. 454
uri (formats)................................................................................... 455
value (columns).................................................................................. 455
vhdr (extensions)................................................................................. 455
vmrk (extensions)................................................................................ 455
volume_type (columns)............................................................................. 456
wavelength_actual (columns).......................................................................... 456
wavelength_emission_actual (columns).................................................................... 456
wavelength_nominal (columns)......................................................................... 456
whole_blood_radioactivity (columns)..................................................................... 457
x sense 1 (columns)................................................................................ 457
x sense 2 (columns)................................................................................ 457
y sense 1 (columns)................................................................................ 458
y sense 2 (columns)................................................................................ 458
z sense 1 (columns)................................................................................ 458
z sense 2 (columns)................................................................................ 459
```
BIDS Extension Proposals 460

Contributors 461

Licenses 470

Entity table 471
Magnetic Resonance Imaging.......................................................................... 471
Biopotential Amplification (EEG and iEEG).................................................................. 473
Magnetoencephalography (MEG)........................................................................ 474
Positron Emission Tomography (PET)..................................................................... 474
Behavioral Data................................................................................. 475
Microscopy.................................................................................... 475

Entities 476
sub......................................................................................... 476
ses......................................................................................... 476
sample....................................................................................... 477


```
task........................................................................................ 477
acq......................................................................................... 477
ce......................................................................................... 478
trc......................................................................................... 478
stain........................................................................................ 478
rec......................................................................................... 478
dir......................................................................................... 479
run......................................................................................... 479
mod........................................................................................ 479
echo........................................................................................ 479
flip......................................................................................... 480
inv......................................................................................... 480
mt......................................................................................... 480
part........................................................................................ 480
proc........................................................................................ 481
hemi........................................................................................ 481
space....................................................................................... 481
split........................................................................................ 482
recording..................................................................................... 482
chunk....................................................................................... 482
atlas........................................................................................ 482
res......................................................................................... 483
den........................................................................................ 483
label........................................................................................ 483
desc........................................................................................ 483
```
File collections 484
Magnetic Resonance Imaging.......................................................................... 484
Anatomy imaging data.......................................................................... 484
Fieldmap data............................................................................... 486

Units 489
Unit table..................................................................................... 489
Prefixes...................................................................................... 490
Multiples.................................................................................. 490
Submultiples................................................................................ 491

Hierarchical Event Descriptors 492
HED annotations and vocabulary........................................................................ 492
Annotating events................................................................................ 492
Annotation using theHEDcolumn........................................................................ 494


```
HED and the BIDS inheritance principle.................................................................... 494
HED schema versions.............................................................................. 494
Using HED library schemas........................................................................ 495
```
MEG file formats 496
CTF........................................................................................ 496
Neuromag/Elekta/MEGIN............................................................................ 497
Cross-talk and fine-calibration files.................................................................... 497
Sharing FIFF data after signal-space separation (SSS)......................................................... 498
Split files.................................................................................. 499
Recording dates in.fiffiles....................................................................... 499
BTi/4D neuroimaging.............................................................................. 499
KIT/Yokogawa/Ricoh.............................................................................. 500
KRISS....................................................................................... 501
ITAB....................................................................................... 502
Aalto MEG–MRI................................................................................. 502

MEG systems 503

Coordinate systems 504
Introduction................................................................................... 504
Coordinate Systems applicable to MEG, EEG, and iEEG........................................................... 505
Commonly used anatomical landmarks in MEG, EEG, and iEEG research.............................................. 505
MEG Specific Coordinate Systems..................................................................... 505
EEG Specific Coordinate Systems..................................................................... 506
iEEG Specific Coordinate Systems..................................................................... 506
Image-based Coordinate Systems........................................................................ 507
Standard template identifiers....................................................................... 507
Nonstandard coordinate system identifiers................................................................ 509
Non-template coordinate system identifiers............................................................... 510

Quantitative MRI 511
Organization of qMRI data in BIDS....................................................................... 511
Inputs are file collections.......................................................................... 511
Quantitative maps are derivatives.................................................................... 512
Example datasets.............................................................................. 513
Metadata requirements for qMRI data..................................................................... 513
Method-specific priority levels for qMRI file collections......................................................... 513
Metadata requirements for qMRI maps................................................................. 514
Deriving the intended qMRI application from an ambiguous file collection................................................. 517
Introducing a new qMRI file collection..................................................................... 518


```
Application-specific notes for qMRI file collections.............................................................. 519
Anatomy imaging data.......................................................................... 519
Radiofrequency (RF) field mapping................................................................... 520
```
Arterial Spin Labeling 523
Which image iscontroland which islabel?................................................................. 523
*_aslcontext.tsv: three possible cases.................................................................... 523
Case 1:*_asl.nii[.gz]consists of volume_typescontrol,label.................................................. 523
Case 2:*_asl.nii[.gz]consists of volume_typesdeltam(scanner does not exportcontrolorlabelvolumes)......................... 524
Case 3:*_asl.nii[.gz]consists of volume_typecbf(scanner does not exportcontrol,label, ordeltaMvolumes)...................... 524
Summary Image of the most common ASL sequences............................................................. 524
(P)CASL sequence............................................................................. 525
(P)CASL Labeling Pulses.......................................................................... 526
PASL sequence............................................................................... 527
Flowchart (based on dependency table).................................................................... 529

Cross modality correspondence 531
PET-MRI correspondence............................................................................ 531

Changelog 532
v1.8.0 (2022-10-29)................................................................................ 532
v1.7.0 (2022-02-15)................................................................................ 533
v1.6.0 (2021-04-22)................................................................................ 535
v1.5.0 (2021-02-23)................................................................................ 536
v1.4.1 (2020-10-13)................................................................................ 537
v1.4.0 (2020-06-11)................................................................................ 538
v1.3.0 (2020-04-14)................................................................................ 539
v1.2.2 (2020-02-12)................................................................................ 539
v1.2.1 (2019-08-14)................................................................................ 540
v1.2.0 (2019-03-04)................................................................................ 542
v1.1.2 (2019-01-10)................................................................................ 542
1.1.1 (2018-06-06)................................................................................. 543
1.1.0 (2018-04-19)................................................................................. 543
1.0.2 (2017-07-18)................................................................................. 544
1.0.1 (2017-03-13)................................................................................. 544
1.0.1-rc1...................................................................................... 544
1.0.0 (2016-06-23)................................................................................. 545
1.0.0-rc4...................................................................................... 545
1.0.0-rc3...................................................................................... 545
1.0.0-rc2...................................................................................... 545
1.0.0-rc1...................................................................................... 546


## The Brain Imaging Data Structure

The Brain Imaging Data Structure (BIDS) is a simple and intuitive way to organize and describe data.

This document defines the BIDS specification, which provides many details to help implement the standard. It includes the core specification as well as many extensions
to specific brain imaging modalities, and increasingly also to other kinds of data.

IfBIDSisnewtoyou,andyouwouldliketolearnmoreabouthowtoadaptyourowndatasetstomatchtheBIDSspecification,werecommendexploringtheBIDSStarter
Kit. Alternatively, to get started please read the introduction to the specification.

For an overview of the BIDS ecosystem, visit theBIDS homepage. The entire specification can also bedownloaded as PDF.


## Introduction

### Motivation

Neuroimaging experiments result in complicated data that can be arranged in many different ways. So far there is no consensus how to organize and share data obtained
in neuroimaging experiments. Even two researchers working in the same lab can opt to arrange their data in a different way. Lack of consensus (or a standard) leads to
misunderstandings and time wasted on rearranging data or rewriting scripts expecting certain structure. Here we describe a simple and easy-to-adopt way of organising
neuroimaging and behavioral data. By using this standard you will benefit in the following ways:

- It will be easy for another researcher to work on your data. To understand the organisation of the files and their format you will only need to refer them to this
    document. This is especially important if you are running your own lab and anticipate more than one person working on the same data over time. By using BIDS
    you will save time trying to understand and reuse data acquired by a graduate student or postdoc that has already left the lab.
- There are a growing number of data analysis software packages that can understand data organised according to BIDS (see theup to date list).
- Databases such asOpenNeuro.orgaccept datasets organised according to BIDS. If you ever plan to share your data publicly (nowadays some journals require this)
    you can minimize the additional time and energy spent on publication, and speed up the curation process by using BIDS to structure and describe your data right
    after acquisition.
- Validation tools such as theBIDS Validatorcan check your dataset integrity and help you easily spot missing values.

BIDS was heavily inspired by the format used internally by the OpenfMRI repository that is now known asOpenNeuro.org, and has been supported by the International
Neuroinformatics Coordinating Facility (INCF) and the INCF Neuroimaging Data Sharing (NIDASH) Task Force. While working on BIDS we consulted many neuroscien-
tists to make sure it covers most common experiments, but at the same time is intuitive and easy to adopt. The specification is intentionally based on simple file formats
and directory structures to reflect current lab practices and make it accessible to a wide range of scientists coming from different backgrounds.

### Extensions

The BIDS specification can be extended in a backwards compatible way and will evolve over time. This is accomplished through community-driven BIDS Extension
Proposals (BEPs). For more information about the BEP process, see Extending the BIDS specification.


### Citing BIDS

WhenreferringtoBIDSincontextofacademicliterature,pleaseciteoneormoreofthepublicationslistedbelow. WeRECOMMENDthatyoucitetheoriginalpublication
on BIDS and additionally the publication regarding the datatype you were using (for example, EEG, MEG, iEEG, if available).
For example:
The data used in the study were organized using the Brain Imaging Data Structure (Gorgolewski, K., Auer, T., Calhoun, V. et al., 2016) with the extension for
EEG data (Pernet, C.R., Appelhoff, S., Gorgolewski, K.J. et al., 2019).

#### Original publication

- Gorgolewski, K.J., Auer, T., Calhoun, V.D., Craddock, R.C., Das, S., Duff, E.P., Flandin, G., Ghosh, S.S., Glatard, T., Halchenko, Y.O., Handwerker, D.A., Hanke, M.,
    Keator, D., Li, X., Michael, Z., Maumet, C., Nichols, B.N., Nichols, T.E., Pellman, J., Poline, J.-B., Rokem, A., Schaefer, G., Sochat, V., Triplett, W., Turner, J.A.,
    Varoquaux, G., Poldrack, R.A. (2016). The brain imaging data structure, a format for organizing and describing outputs of neuroimaging experiments. Scientific
    Data, 3 (160044).doi:10.1038/sdata.2016.44

#### Datatype specific publications.

##### EEG

- Pernet, C. R., Appelhoff, S., Gorgolewski, K.J., Flandin, G., Phillips, C., Delorme, A., Oostenveld, R. (2019). EEG-BIDS, an extension to the brain imaging data
    structure for electroencephalography. Scientific data, 6 (103).doi:10.1038/s41597-019-0104-8

```
iEEG
```
- Holdgraf,C.,Appelhoff,S.,Bickel,S.,Bouchard,K.,D’Ambrosio,S.,David,O.,Devinsky,O.,Dichter,B.,Flinker,A.,Foster,B.L.,Gorgolewski,K.J.,Groen,I.,Groppe,
    D., Gunduz, A., Hamilton, L., Honey, C. J., Jas, M., Knight, R., Lauchaux, J.-P., Lau, J. C., Lee-Messer, C., Lundstrom, B. N., Miller, K. J., Ojemann, J. G., Oostenveld,
    R., Petridou, N., Piantoni, G., Pigorini, A., Pouratian, N., Ramsey, N. F., Stolk, A., Swann, N. C., Tadel, F., Voytek, B., Wandell, B. A., Winawer, J., Whitaker, K.,
    Zehl, L., Hermes, D. (2019). iEEG-BIDS, extending the Brain Imaging Data Structure specification to human intracranial electrophysiology. Scientific data, 6 (102).
    doi:10.1038/s41597-019-0105-7

##### MEG

- Niso Galan, J.G., Gorgolewski, K.J., Bock, E., Brooks, T.L., Flandin, G., Gramfort, A., Henson, R.N., Jas, M., Litvak, V., Moreau, J., Oostenveld, R., Schoffelen,
    J.-M., Tadel, F., Wexler, J., Baillet, S. (2018). MEG-BIDS, the brain imaging data structure extended to magnetoencephalography. Scientific Data, 5 (180110).
    doi:10.1038/sdata.2018.110

##### PET

- Norgaard, M., Matheson, G.J., Hansen, H.D., Thomas, A., Searle, G., Rizzo, G., Veronese, M., Giacomel, A., Yaqub, M., Tonietto, M., Funck, T., Gillman, A., Boniface,
    H., Routier, A., Dalenberg, J.R.., Betthauser, T., Feingold, F., Markiewicz, C.J., Gorgolewski, K.J., Blair, R.W., Appelhoff, S., Gau, R., Salo, T., Niso, G., Pernet, C.,


```
Phillips, C., Oostenveld, R., Gallezot, J-D., Carson, R.E., Knudsen, G.M., Innis R.B. & Ganz M. (2021). PET-BIDS, an extension to the brain imaging data structure
for positron emission tomography. Scientific Data, 9 (65).doi:10.1038/s41597-022-01164-1
```
- Knudsen GM, Ganz M, Appelhoff S, Boellaard R, Bormans G, Carson RE, Catana C, Doudet D, Gee AD, Greve DN, Gunn RN, Halldin C, Herscovitch P, Huang H,
    KellerSH,LammertsmaAA,LanzenbergerR,LiowJS,LohithTG,LubberinkM,LyooCH,MannJJ,MathesonGJ,NicholsTE,NørgaardM,OgdenT,ParseyR,Pike
    VW,PriceJ,RizzoG,Rosa-NetoP,SchainM,ScottPJH,SearleG,SlifsteinM,SuharaT,TalbotPS,ThomasA,VeroneseM,WongDF,YaqubM,ZanderigoF,Zoghbi
    S, Innis RB. (2020). Guidelines for Content and Format of PET Brain Data in Publications and in Archives: A Consensus Paper. Journal of Cerebral Blood Flow and
    Metabolism, 2020 Aug; 40(8): 1576-1585.doi:10.1177/0271678X20905433

Genetics

- Clara Moreau, Martineau Jean-Louis, Ross Blair, Christopher Markiewicz, Jessica Turner, Vince Calhoun, Thomas Nichols, Cyril Pernet (2020). The genetics-BIDS
    extension: Easing the search for genetic data associated with human brain imaging. GigaScience, 9 (10).doi:10.1093/gigascience/giaa104

Microscopy

- Bourget M.-H., Kamentsky L., Ghosh S.S., Mazzamuto G., Lazari A., Markiewicz C.J., Oostenveld R., Niso G., Halchenko Y.O., Lipp I., Takerkart S., Toussaint P.-J.,
    Khan A.R., Nilsonne G., Castelli F.M., The BIDS Maintainers and Cohen-Adad J. (2022). Microscopy-BIDS: An Extension to the Brain Imaging Data Structure for
    Microscopy Data. Frontiers in Neuroscience, 16 (871228).doi:10.3389/fnins.2022.871228

qMRI

- Karakuzu, A., Appelhoff, S., Auer, T., Boudreau M., Feingold F., Khan A.R., Lazari A., Markiewicz C.J., Mulder M., Phillips C., Salo T., Stikov N., Whitaker K. and
    de Hollander G., qMRI-BIDS: An extension to the brain imaging data structure for quantitative magnetic resonance imaging data. Scientific Data 9, 517 (2022).
    doi:10.1038/s41597-022-01571-4

##### NIRS

- (publication forthcoming)

#### Research Resource Identifier (RRID)

BIDS has also aResearch Resource Identifier (RRID), which you can also include in your citations in addition to relevant publications (see above):

- RRID:SCR_016124


## Common principles

### Definitions

The keywords ”MUST”, ”MUST NOT”, ”REQUIRED”, ”SHALL”, ”SHALL NOT”, ”SHOULD”, ”SHOULD NOT”, ”RECOMMENDED”, ”MAY”, and ”OPTIONAL” in this
document are to be interpreted as described in [RFC2119].

Throughout this specification we use a list of terms and abbreviations. To avoid misunderstanding we clarify them here.

1. Dataset - A set of neuroimaging and behavioral data acquired for a purpose of a particular study. A dataset consists of data acquired from one or more subjects,
    possibly from multiple sessions.
2. Modality - The category of brain data recorded by a file. For MRI data, different pulse sequences are considered distinct modalities, such asT1w,boldordwi. For
    passive recording techniques, such as EEG, MEG or iEEG, the technique is sufficiently uniform to define the modalitieseeg,megandieeg. When applicable, the
    modality is indicated in the suffix. The modality may overlap with, but should not be confused with the data type.
3. Data type - A functional group of different types of data. Data files are contained in a directory named for the data type. In raw datasets, the data type directory is
    nested inside subject and (optionally) session directories. BIDS defines the following data types:
       (a)func(task based and resting state functional MRI)
       (b)dwi(diffusion weighted imaging)
          (c)fmap(field inhomogeneity mapping data such as field maps)
       (d)anat(structural imaging such as T1, T2, PD, and so on)
          (e)perf(perfusion)
          (f)meg(magnetoencephalography)
       (g)eeg(electroencephalography)
(h) ieeg(intracranial electroencephalography)
(i) beh(behavioral)


```
(j) pet(positron emission tomography)
(k)micr(microscopy)
(l) nirs(near infrared spectroscopy)
```
4. Subject - A person or animal participating in the study. Used interchangeably with term Participant.
5. Session-Alogicalgroupingofneuroimagingandbehavioraldataconsistentacrosssubjects. Sessioncan(butdoesn’thaveto)besynonymoustoavisitinalongitudi-
    nalstudy. Ingeneral,subjectswillstayinthescannerduringonesession. However,forexample,ifasubjecthastoleavethescannerroomandthenbere-positioned
    on the scanner bed, the set of MRI acquisitions will still be considered as a session and match sessions acquired in other subjects. Similarly, in situations where
    different data types are obtained over several visits (for example fMRI on one day followed by DWI the day after) those can be grouped in one session. Defining
    multiple sessions is appropriate when several identical or similar data acquisitions are planned and performed on all -or most- subjects, often in the case of some
    intervention between sessions (for example, training). In the PET context, a session may also indicate a group of related scans, taken in one or more visits.
6. Sample-Asamplepertainingtoasubjectsuchastissue,primarycellorcell-freesample. SamplelabelsMUSTbeuniquewithinasubjectanditisRECOMMENDED
    that they be unique throughout the dataset.
7. Data acquisition - A continuous uninterrupted block of time during which a brain scanning instrument was acquiring data according to particular scanning se-
    quence/protocol.
8. Task - A set of structured activities performed by the participant. Tasks are usually accompanied by stimuli and responses, and can greatly vary in complexity.
    For the purpose of this specification we consider the so-called ”resting state” a task. In the context of brain scanning, a task is always tied to one data acquisition.
    Therefore,evenifduringoneacquisitionthesubjectperformedmultipleconceptuallydifferentbehaviors(withdifferentsetsofinstructions)theywillbeconsidered
    one (combined) task.
9. Event - Something that happens or may be perceived by a test subject as happening at a particular instant during the recording. Events are most commonly
    associated with on- or offset of stimulus presentations, or with the distinct marker of on- or offset of a subject’s response or motor action. Other events may include
    unplanned incidents (for example, sudden onset of noise and vibrations due to construction work, laboratory device malfunction), changes in task instructions (for
    example, switching the response hand), or experiment control parameters (for example, changing the stimulus presentation rate over experimental blocks), and
    noteddatafeatureoccurrences(forexample,arecordingelectrodeproducingnoise). InBIDS,eacheventhasanonsettimeandduration. Notethatnotalltaskswill
    have recorded events (for example, ”resting state”).
10. Run-Anuninterruptedrepetitionofdataacquisitionthathasthesameacquisitionparametersandtask(howevereventscanchangefromruntorunduetodifferent
subject response or randomized nature of the stimuli). Run is a synonym of a data acquisition. Note that ”uninterrupted” may look different by modality due to
the nature of the recording. For example, in MRI or MEG, if a subject leaves the scanner, the acquisition must be restarted. For some types of PET acquisitions, a
subject may leave and re-enter the scanner without interrupting the scan.
11. index - A nonnegative integer, possibly prefixed with arbitrary number of 0s for consistent indentation, for example, it is 01 inrun-01followingrun-<index>
specification.
12. label-Analphanumericvalue,possiblyprefixedwitharbitrarynumberof0sforconsistentindentation,forexample,itisrestintask-restfollowingtask-<label>
specification. Note that labels MUST not collide when casing is ignored (see Case collision intolerance).
13. suffix - An alphanumeric string that forms part of a filename, located after all entities and following a final_, right before the file extension; for example, it iseeg
insub-05_task-matchingpennies_eeg.vhdr.


14. Fileextension-Aportionofthefilenameaftertheleft-mostperiod(.) precededbyanyotheralphanumeric. Forexample,.gitignoredoesnothaveafileextension,
    but the file extension oftest.nii.gzis.nii.gz. Note that the left-most period is included in the file extension.
15. DEPRECATED-A”deprecated”entityormetadatafieldSHOULDNOTbeusedinthegenerationofnewdatasets. Itremainsinthestandardinordertopreservethe
    interpretability of existing datasets. Validating software SHOULD warn when deprecated practices are detected and provide a suggestion for updating the dataset
    to preserve the curator’s intent.

### Entities

```
An”entity”isanattributethatcanbeassociatedwithafile,contributingtotheidentificationofthatfileasacomponentofitsfilenameintheformofahyphen-separated
key-value pair.
Each entity has the following attributes:
```
1. Name: A comprehensive name describing the context of information to be provided via the entity.
2. Key: A short string, typically a compression of the entity name, which uniquely identifies the entity when part of a filename.
3. Value type: The requisite form of the value that gets specified alongside the key whenever the entity appears in a filename. For each entity, the value is of one of
    two possible types:
       (a)Index: A non-negative integer, potentially zero-padded for consistent width.
       (b)Label: An alphanumeric string. Note that labels MUST not collide when casing is ignored (see Case collision intolerance).
The entity format is a string that prescribes how the entity appears within any given filename. For a hypothetical entity with key ”key”, the format can be either
”key-<index>” or ”key-<label>”, depending on the value type of that entity.

```
An entity instance is the specific manifestation of an entity within the name of a specific file, based on the format of the entity but with a value that provides identifying
information to the particular file in whose name it appears.
Depending on context, any one of the entity name, key, format, or a specific entity instance, may be referred to as simply an ”entity”.
```
”Subject”, ”session”, ”sample”, ”task”, and ”run” from the list of definitions above are all examples of entities. The comprehensive list of supported entities is defined in
the Entities Appendix; further, whether each is OPTIONAL, REQUIRED, or MUST NOT be provided for various data files, as well as their relative ordering in a filename,
are defined in the Entity Tables Appendix.

### Compulsory, optional, and additional data and metadata

```
The following standard describes a way of arranging data and writing down metadata for a subset of neuroimaging experiments. Some aspects of the standard are
compulsory. For example a particular filename format is required when storing structural scans. Some aspects are regulated but optional. For example a T2 volume does
not need to be included, but when it is available it should be saved under a particular filename specified in the standard. This standard aspires to describe a majority
of datasets, but acknowledges that there will be cases that do not fit. In such cases one can include additional files and subdirectories to the existing directory structure
followingcommonsense. Forexampleonemaywanttoincludeeyetrackingdatainavendorspecificformatthatisnotcoveredbythisstandard. Themostsensibleplace
```

```
to put it is next to the continuous recording file with the same naming scheme but different extensions. The solutions will change from case to case and publicly available
datasets will be reviewed to include common data types in the future releases of the BIDS specification.
It is RECOMMENDED that non-compulsory metadata fields (likenotchinchannels.tsvfiles) and/or files (likeevents.tsv) are fully omitted when they are unavailable
or unapplicable, instead of specified with ann/avalue, or included as an empty file (for example an emptyevents.tsvfile with only the headers included).
```
### Filesystem structure

```
Data for each subject are placed in subdirectories named ”sub-<label>”, where string ”<label>” is substituted with the unique identification label of each subject.
Additional information on each participant MAY be provided in a participants file in the root directory of the dataset.
If data for the subject were acquired across multiple sessions, then within the subject directory resides subdirectories named ”ses-<label>”, where string ”<label>” is
substitutedwithauniqueidentificationlabelforeachsession. Indatasetswhereatleastonesubjecthasmorethanonesession,thisadditionalsubdirectorylaterSHOULD
be added for all subjects in the dataset. Additional information on each session MAY be provided in a sessions file within the subject directory.
```
Within the session subdirectory (or the subject subdirectory if no session subdirectories are present) are subdirectories named according to data type as defined above. A
data type directory SHOULD NOT be defined if there are no files to be placed in that directory.

#### Other top level directories

```
In addition to the subject directories, the root directory of a BIDS dataset MAY also contain the following directories:
```
- code: A directory in which to store any code (for example the one used to generate the derivatives from the raw data). See the Code section for more information.
- derivatives: Derivative data (for example preprocessed files). See the relevant section for more information.
- sourcedata: A directory where to store data before harmonization, reconstruction, and/or file format conversion (for example, E-Prime event logs or DICOM files).
    See the relevant section for more information.
- stimuli: A directory to store any stimulus files used during an experiment. See the relevant section for more information.

### Filenames.

```
A filename consists of a chain of entity instances and a suffix all separated by underscores, and an extension. This pattern forms filenames that are both human- and
machine-readable. Forinstance,file”sub-01_task-rest_eeg.edf”containsinstancesofthe”subject”and”task”entities,makingitevidentfromthefilenamealonethat
it contains resting-state data from subject 01 ; the suffixeegand extension.edfdepend on the imaging modality and the data format, and can therefore convey further
details of the file’s contents.
For a data file that was collected in a given session from a given subject, the filename MUST begin with the stringsub-<label>_ses-<label>. Conversely, if the session
level is omitted in the directory structure, the file name MUST begin with the stringsub-<label>, withoutses-<label>.
Any given entity MUST NOT appear more than once in any filename. For example, filename ”sub-01_acq-laser_acq-uneven_electrodes.tsv” is invalid because it
uses the ”acquisition” entity twice.
```

In cases where an entity and a metadata field convey similar contextual information, the presence of an entity should not be used as a replacement for the corresponding
metadatafield. Forinstance,inecho-planarimagingMRI,thedir-<label>entityMAYbeusedtodistinguishfileswithdifferentphase-encodingdirections, butthefile’s
PhaseEncodingDirectionMUST be specified as metadata.

A summary of all entities in BIDS and the order in which they MUST be specified is available in the entity table in the appendix.

#### Entity-linked file collections.

Anentity-linkedfilecollectionisasetoffilesthatarerelatedtoeachotherbasedonarepetitiveacquisitionofsequentialdatabychangingacquisitionparametersone(or
multiple)atatimeorbybeinginherentcomponentsofthesamedata. Entity-linkedcollectionsareidentifiedbyacommonsuffix,indicatingthegroupoffilesthatshould
be considered a logical unit. Within each collection, files MUST be distinguished from each other by at least one entity (for example,echo) that corresponds to an altered
acquisition parameter (EchoTime) or that defines a component relationship (for example,part). Note that these entities MUST be described by the specification and the
parameter changes they declare MUST NOT invalidate the definition of the accompanying suffix. For example, the use of theechoentity along with theT1wsuffix casts
doubtonthevalidityoftheidentifiedcontrastweighting. Providedtheconditionsabovearesatisfied,anysuffix(suchasbold)canidentifyanentity-linkedfilecollection,
although certain suffixes are exclusive for this purpose (for example,MP2RAGE). Use cases concerning this convention are compiled in the file collections appendix. This
convention is mainly intended for but not limited to MRI modalities.

#### Case collision intolerance

File name components are case sensitive, but collisions MUST be avoided when casing is ignored. For example, a dataset cannot contain bothsub-s1andsub-S1, as the
labelswouldcollideonacase-insensitivefilesystem. Additionally,becausethesuffixeegisdefined,thenthesuffixEEGwillnotbeaddedtofutureversionsofthestandard.

### Source vs. raw vs. derived data

BIDSwasoriginallydesignedtodescribeandapplyconsistentnamingconventionstoraw(unprocessedorminimallyprocessedduetofileformatconversion)data. During
analysis such data will be transformed and partial as well as final results will be saved. Derivatives of the raw data (other than products of DICOM to NIfTI conversion)
MUST be kept separate from the raw data. This way one can protect the raw data from accidental changes by file permissions. In addition it is easy to distinguish partial
results from the raw data and share the latter. See Storage of derived datasets for more on organizing derivatives.

Similarrulesapplytosourcedata,whichisdefinedasdatabeforeharmonization,reconstruction,and/orfileformatconversion(forexample,E-PrimeeventlogsorDICOM
files). Storing actual source files with the data is preferred over links to external source repositories to maximize long term preservation, which would suffer if an external
repository would not be available anymore. This specification currently does not go into the details of recommending a particular naming scheme for including different
types of source data (such as the raw event logs or parameter files, before conversion to BIDS). However, in the case that these data are to be included:

1. These data MUST be kept in separatesourcedatadirectory with a similar directory structure as presented below for the BIDS-managed data. For example:
    sourcedata/sub-01/ses-pre/func/sub-01_ses-pre_task-rest_bold.dicom.tgzorsourcedata/sub-01/ses-pre/func/MyEvent.sce.
2. AREADMEfileSHOULDbefoundattherootofthesourcedatadirectoryorthederivativesdirectory,orboth. Thisfileshoulddescribethenatureoftherawdata
    or the derived data. We RECOMMEND including the PDF print-out with the actual sequence parameters generated by the scanner in thesourcedatadirectory.

Alternatively one can organize their data in the following way

```
my_dataset-1/
```

```
sourcedata
```
```
rawdata/
dataset_description.json
participants.tsv
sub-01/
sub-02/
```
```
derivatives/
pipeline_1/
pipeline_2/
```
In this example, wheresourcedataandderivativesare not nested insiderawdata, only the **rawdata** subdirectory needs to be a BIDS-compliant dataset. The subdirec-
toriesofderivativesMAYbeBIDS-compliantderivativesdatasets(seeNon-compliantderivativesforfurtherdiscussion). Thisspecificationdoesnotprescribeanything
aboutthecontentsofsourcedatadirectoriesintheaboveexample-nordoesitprescribethesourcedata,derivatives,orrawdatadirectorynames. Theaboveexample
is just a convention that can be useful for organizing raw, source, and derived data while maintaining BIDS compliance of the raw data directory. When using this
convention it is RECOMMENDED to set theSourceDatasetsfield indataset_description.jsonof each subdirectory ofderivativesto:

{
"SourceDatasets": [{"URL": "file://../../rawdata/"} ]
}

#### Storage of derived datasets

Derivatives can be stored/distributed in two ways:

1. Under aderivatives/subdirectory in the root of the source BIDS dataset directory to make a clear distinction between raw data and results of data processing. A
    data processing pipeline will typically have a dedicated directory under which it stores all of its outputs. Different components of a pipeline can, however, also be
    stored under different subdirectories. There are few restrictions on the directory names; it is RECOMMENDED to use the format<pipeline>-<variant>in cases
    where it is anticipated that the same pipeline will output more than one variant (for example,AFNI-blurringandAFNI-noblurring). For the sake of consistency,
    the subdirectory name SHOULD be theGeneratedBy.Namefield indata_description.json, optionally followed by a hyphen and a suffix (see Derived dataset and
    pipeline description).
    Example of derivatives with one directory per pipeline:
    <dataset>/derivatives/fmriprep-v1.4.1/sub-0001
    <dataset>/derivatives/spm/sub-0001
    <dataset>/derivatives/vbm/sub-0001
    Example of a pipeline with split derivative directories:
    <dataset>/derivatives/spm-preproc/sub-0001
    <dataset>/derivatives/spm-stats/sub-0001


```
Example of a pipeline with nested derivative directories:
<dataset>/derivatives/spm-preproc/sub-0001
<dataset>/derivatives/spm-preproc/derivatives/spm-stats/sub-0001
```
2. Asastandalonedatasetindependentofthesource(raworderived)BIDSdataset. Thiswayofspecifyingderivativesisparticularlyusefulwhenthesourcedatasetis
    providedwithread-onlyaccess,forpublishingderivativesasindependentbodiesofwork,orfordescribingderivativesthatwerecreatedfrommorethanonesource
    dataset. Thesourcedata/subdirectoryMAYbeusedtoincludethesourcedataset(s)thatwereusedtogeneratethederivatives. Likewise,anycodeusedtogenerate
    the derivatives from the source data MAY be included in thecode/subdirectory.
    Example of a derivative dataset including the raw dataset as source:
my_processed_data/
code/
processing_pipeline-1.0.0.img
hpc_submitter.sh

```
sourcedata/
sub-01/
sub-02/
```
```
sub-01/
sub-02/
```
Throughout this specification, if a section applies particularly to derivatives, then Case 1 will be assumed for clarity in templates and examples, but removing
/derivatives/<pipeline>from the template name will provide the equivalent for Case 2. In both cases, every derivatives dataset is considered a BIDS dataset and
must include adataset_description.jsonfile at the root level (see Dataset description). Consequently, files should be organized to comply with BIDS to the full extent
possible (that is, unless explicitly contradicted for derivatives). Any subject-specific derivatives should be housed within each subject’s directory; if session-specific
derivatives are generated, they should be deposited under a session subdirectory within the corresponding subject directory; and so on.

#### Non-compliant derivatives

Nothing in this specification should be interpreted to disallow the storage/distribution of non-compliant derivatives of BIDS datasets. In particular, if a BIDS dataset
contains aderivatives/subdirectory, the contents of that directory may be a heterogeneous mix of BIDS Derivatives datasets and non-compliant derivatives.

### File Formation specification.

#### Imaging files

All imaging data MUST be stored using the NIfTI file format. We RECOMMEND using compressed NIfTI files (.nii.gz), either version 1.0 or 2.0. Imaging data SHOULD
be converted to the NIfTI format using a tool that provides as much of the NIfTI header information (such as orientation and slice timing information) as possible. Since
the NIfTI standard offers limited support for the various image acquisition parameters available in DICOM files, we RECOMMEND that users provide additional meta


information extracted from DICOM files in a sidecar JSON file (with the same filename as the.nii[.gz]file, but with a.jsonextension). Extraction of BIDS compatible
metadata can be performed usingdcm2niixanddicm2niiDICOM to NIfTI converters. TheBIDS-validatorwill check for conflicts between the JSON file and the data
recorded in the NIfTI header.

#### Tabular files

TabulardataMUSTbesavedastabdelimitedvalues(.tsv)files,thatis,CSVfileswherecommasarereplacedbytabs. TabsMUSTbetruetabcharactersandMUSTNOT
be a series of space characters. Each TSV file MUST start with a header line listing the names of all columns (with the exception of physiological and other continuous
recordings). It is RECOMMENDED that the column names in the header of the TSV file are written insnake_casewith the first letter in lower case (for example,
variable_name, notVariable_name). As for all other data in the TSV files, column names MUST be separated with tabs. Furthermore, column names MUST NOT be
blank (that is, an empty string) and MUST NOT be duplicated within a single TSV file. String values containing tabs MUST be escaped using double quotes. Missing and
non-applicable values MUST be coded asn/a. Numerical values MUST employ the dot (.) as decimal separator and MAY be specified in scientific notation, usingeorE
to separate the significand from the exponent. TSV files MUST be in UTF-8 encoding.

Example:

onset duration response_time correct stop_trial go_trial
200 200 0 n/a n/a n/a

Note: The TSV examples in this document (like the one above this note) are occasionally formatted using space characters instead of tabs to improve human readability.
Directly copying and then pasting these examples from the specification for use in new BIDS datasets can lead to errors and is discouraged.

TabularfilesMAYbeoptionallyaccompaniedbyasimpledatadictionaryintheformofaJSONobjectwithinaJSONfile. TheJSONfilescontainingthedatadictionaries
MUST have the same name as their corresponding tabular files but with.jsonextensions. If a data dictionary is provided, it MAY contain one or more fields describing
the columns found in the TSV file (in addition to any other metadata one wishes to include that describe the file as a whole). Note that if a field name included in the
datadictionarymatchesacolumnnameintheTSVfile, thenthatfieldMUSTcontainadescriptionofthecorrespondingcolumn, usinganobjectcontainingthefollowing
fields:

Key name Requirement Level Data type Description

LongName OPTIONAL string Long (unabbreviated) name of the
column.
Description RECOMMENDED string Free-form natural language description.
The description of the column.
Levels RECOMMENDED objectofstrings For categorical variables: An object of
possible values (keys) and their
descriptions (values).
Units RECOMMENDED string Measurement units for the associated
file. SI units in CMIXF formatting are
RECOMMENDED (see Units).
TermURL RECOMMENDED string URL pointing to a formal definition of
this type of data in an ontology
available on the web.


Key name Requirement Level Data type Description

HED OPTIONAL stringorobjectofstrings Hierarchical Event Descriptor (HED)
information, see the HED for details.

Please note that while bothUnitsandLevelsare RECOMMENDED, typically only one of these two fields would be specified for describing a single TSV file column.

Example:

{
"test":{
"LongName": "Education level",
"Description":"Education level, self-rated by participant",
"Levels":{
"1": "Finished primary school",
"2": "Finished secondary school",
"3": "Student at university",
"4": "Has degree from university"
}
},
"bmi":{
"LongName": "Body mass index",
"Units":"kg/m^2",
"TermURL":"https://purl.bioontology.org/ontology/SNOMEDCT/60621009"
}
}

#### Key-value files (dictionaries)

JavaScript Object Notation (JSON) files MUST be used for storing key-value pairs. JSON files MUST be in UTF-8 encoding. Extensive documentation of the format can
be found athttps://www.json.org/, and athttps://tools.ietf.org/html/std90. Several editors have built-in support for JSON syntax highlighting that aids manual creation
of such files. An online editor for JSON with built-in validation is available athttps://jsoneditoronline.org. It is RECOMMENDED that keys in a JSON file are written in
CamelCasewith the first letter in upper case (for example,SamplingFrequency, notsamplingFrequency). Note however, when a JSON file is used as an accompanying
sidecar file for a TSV file, the keys linking a TSV column with their description in the JSON file need to follow the exact formatting as in the TSV file.

Example of a hypothetical*_bold.jsonfile, accompanying a*_bold.niifile:

{
"RepetitionTime": 3 ,
"Instruction": "Lie still and keep your eyes open"
}


Example of a hypothetical*_events.jsonfile, accompanying an*_events.tsvfile. Note that the JSON file contains a key describing an arbitrary column
stim_presentation_sidein the TSV file it accompanies. See task events section for more information.

{
"stim_presentation_side":{
"Levels":{
"1": "stimulus presented on LEFT side",
"2": "stimulus presented on RIGHT side"
}
}
}

### The Inheritance Principle

1. Any metadata file (such as.json,.bvecor.tsv) MAY be defined at any directory level.
2. For a given data file, any metadata file is applicable to that data file if:
    (a)It is stored at the same directory level or higher;
    (b)The metadata and the data filenames possess the same suffix;
       (c)The metadata filename does not include any entity absent from the data filename.
3. A metadata file MUST NOT have a filename that would be otherwise applicable to some data file based on rules 2.b and 2.c but is made inapplicable based on its
    location in the directory structure as per rule 2.a.
4. There MUST NOT be multiple metadata files applicable to a data file at one level of the directory hierarchy.
5. If multiple metadata files satisfy criteria 2.a-c above:
    (a)Fortabularfilesandothersimplemetadatafiles(forinstance,bvec/bvalfilesfordiffusionMRI),accessingmetadataassociatedwithadatafileMUSTconsider
       only the applicable file that is lowest in the filesystem hierarchy.
    (b)ForJSONfiles, key-valuesareloadedfromfilesfromthetopofthedirectoryhierarchydownwards, suchthatkey-valuesfromthetoplevelareinheritedbyall
       data files at lower levels to which it is applicable unless overridden by a value for the same key present in another metadata file at a lower level (though it is
       RECOMMENDED to minimize the extent of such overrides).

Corollaries:

1. As per rule 3, metadata files applicable only to a specific participant / session MUST be defined in or below the directory corresponding to that participant / session;
    similarly, a metadata file that is applicable to multiple participants / sessions MUST NOT be placed within a directory corresponding to only one such participant /
    session.
2. It is permissible for a single metadata file to be applicable to multiple data files at that level of the hierarchy or below. Where such metadata content is consistent
    across multiple data files, it is RECOMMENDED to store metadata in this way, rather than duplicating that metadata content across multiple metadata files.


3. Where multiple applicable JSON files are loaded as per rule 5.b, key-values can only be overwritten by files lower in the filesystem hierarchy; the absence of a
    key-value in a later file does not imply the ”unsetting” of that field (indeed removal of existing fields is not possible).
Example 1: Demonstration of inheritance principle
sub-01/
func/
sub-01_task-rest_acq-default_bold.nii.gz
sub-01_task-rest_acq-longtr_bold.nii.gz
sub-01_task-rest_acq-longtr_bold.json
task-rest_bold.json
Contents of filetask-rest_bold.json:
{
"EchoTime": 0.040,
"RepetitionTime":1.0
}
Contents of filesub-01/func/sub-01_task-rest_acq-longtr_bold.json:
{
"RepetitionTime":3.0
}

Whenreadingimagesub-01/func/sub-01_task-rest_acq-default_bold.nii.gz,onlymetadatafiletask-rest_bold.jsonisread;filesub-01/func/sub-01_task-rest_acq-longtr_bold.json
isinapplicableasitcontainsentity”acq-longtr”thatisabsentfromtheimagepath(rule2.c). Whenreadingimagesub-01/func/sub-01_task-rest_acq-longtr_bold.nii.gz,
metadatafiletask-rest_bold.jsonatthetoplevelisreadfirst,followedbyfilesub-01/func/sub-01_task-rest_acq-longtr_bold.jsonatthebottomlevel(rule5.b);
the value for field ”RepetitionTime” is therefore overridden to the value3.0. The value for field ”EchoTime” remains applicable to that image, and is not unset by its
absence in the metadata file at the lower level (rule 5.b; corollary 3).
Example 2: Impermissible use of multiple metadata files at one directory level (rule 4)
sub-01/
ses-test/
anat/
sub-01_ses-test_T1w.nii.gz
func/
sub-01_ses-test_task-overtverbgeneration_run-1_bold.nii.gz
sub-01_ses-test_task-overtverbgeneration_run-2_bold.nii.gz
sub-01_ses-test_task-overtverbgeneration_bold.json
sub-01_ses-test_task-overtverbgeneration_run-2_bold.json
Example 3: Modification of filesystem structure from Example 2 to satisfy inheritance principle requirements
sub-01/


```
ses-test/
sub-01_ses-test_task-overtverbgeneration_bold.json
anat/
sub-01_ses-test_T1w.nii.gz
func/
sub-01_ses-test_task-overtverbgeneration_run-1_bold.nii.gz
sub-01_ses-test_task-overtverbgeneration_run-2_bold.nii.gz
sub-01_ses-test_task-overtverbgeneration_run-2_bold.json
```
Example 4: Single metadata file applying to multiple data files (corollary 2)

```
sub-01/
anat/
func/
sub-01_task-xyz_acq-test1_run-1_bold.nii.gz
sub-01_task-xyz_acq-test1_run-2_bold.nii.gz
sub-01_task-xyz_acq-test1_bold.json
```
### Participant names and other labels.

BIDSallowsforcustomuser-defined<label>sand<index>esforexample,fornamingofparticipants, sessions,acquisitionschemes. NotethattheyMUSTconsistonlyof
allowedcharactersasdescribedinDefinitionsabove. In<index>esweRECOMMENDusingzeropadding(forexample, 01 insteadof 1 ifyouhavemorethanninesubjects)
to make alphabetical sorting more intuitive. Note that zero padding SHOULD NOT be used to merely maintain uniqueness of<index>es.

Please note that a given label or index is distinct from the ”prefix” it refers to. For examplesub-01refers to thesubentity (a subject) with the label 01. Thesub-prefix
is not part of the subject label, but must be included in filenames (similarly to other entities).

### Specification of paths

Several metadata fields in BIDS require the specification of paths, that is, a string of characters used to uniquely identify a location in a directory structure. For example
theIntendedFororAssociatedEmptyroommetadata fields.

Throughout BIDS all such paths MUST be specified using the slash character (/), regardless of the operating system that a particular dataset is curated on or used on.

Paths SHOULD NOT be absolute local paths, because these might break when a dataset is used on a different machine. It is RECOMMENDED that all paths specified in a
BIDS dataset are relative paths, as specified in the respective descriptions of metadata fields that require the use of paths.

### Uniform Resource Indicator.

A Uniform Resource Indicator (URI) is a string referring to a resource and SHOULD have the form<scheme>:[//<authority>]<path>[?<query>][#<fragment>], as
specifiedinRFC3986. ThisappliestoURLsandothercommonURIs,includingDigitalObjectIdentifiers(DOIs),whichmaybefullyspecifiedasdoi:<path>,forexample,


doi:10.5281/zenodo.3686061. A given resource may have multiple URIs. When selecting URIs to add to dataset metadata, it is important to consider specificity and
persistence.

SeveralfieldsaredesignatedforDOIs,forexample,DatasetDOIindataset_description.json. DOIvaluesSHOULDbefullyspecifiedURIssuchasdoi:10.18112/openneuro.ds000001.v1.0.0.
Bare DOIs such as10.18112/openneuro.ds000001.v1.0.0are [DEPRECATED][].

#### BIDS URI

To reference files in BIDS datasets, the following URI scheme may be used:

bids:[<dataset-name>]:<relative-path>

The scheme componentbidsidentifies a BIDS URI, which defines apathcomponent of the form<dataset-name>:<relative-path>. Thedataset-namecomponent
is an identifier for a BIDS dataset, and therelative-pathcomponent is the location of a resource within that BIDS dataset, relative to the root of that dataset. The
relative-pathMUST NOT start with a forward-slash character (/).

Examples:

bids::sub-01/fmap/sub-01_dir-AP_epi.nii.gz
bids:ds000001:sub-02/anat/sub-02_T1w.nii.gz
bids:myderivatives:sub-03/func/sub-03_task-rest_space-MNI152_bold.nii.gz

If no dataset name is specified, the URI is relative to the current BIDS dataset. This is made more precise in the next section.

Resolution of BIDS URIs

In order to resolve a BIDS URI, the dataset name must be mapped to a BIDS dataset.

The special case""(that is, the empty string) refers to the BIDS dataset in which the BIDS URI is found. The dataset root is the nearest parent directory that contains a
validdataset_description.json.

All other dataset names MUST be specified in theDatasetLinksobject in [dataset_description.json][], which maps dataset names to URIs that point to BIDS dataset
locations. If the scheme is omitted from a URI inDatasetLinks, that path is resolved relative to the current dataset root (seederiv1example, below).

BIDS URIs cannot be interpreted outside a BIDS dataset, as they require adataset_description.jsonfile to resolve.

Examples

Consider this exampledataset_description.json:

**{**
...
"DatasetLinks" **: {**
"deriv1" **:** "derivatives/derivative1" **,**
"phantoms" **:** "file:///data/phantoms" **,**
"ds000001" **:** "doi:10.18112/openneuro.ds000001.v1.0.0"


##### }

##### }

Herederiv1refers to a BIDS Derivatives dataset contained within the current dataset,phantomsrefers to a BIDS dataset of phantom data stored on the local filesystem,
andds000001refers to a BIDS dataset that must be resolved by DOI.

Notethatresolvingbids:phantoms:sub-phantom01/anat/sub-phantom01_T1w.nii.gzisastraightforwardconcatenation:file:///data/phantoms/sub-phantom01/anat/sub-phantom01_T1w.nii.gz.
However, retrievingbids:ds000001:sub-02/anat/sub-02_T1w.nii.gzrequires first resolving the DOI, identifying the retrieval method, possibly retrieving the entire
dataset, and finally constructing a URI to the desired resource.

No protocol is currently proposed to automatically resolve all possible BIDS URIs.

Future statement

BIDS URIs are parsable as standard [URIs][] with schemebidsand path[<dataset-name>]:<relative-path>. The authority, query and fragment components are
unused. Future versions of BIDS may specify interpretations for these components, but MUST NOT change the interpretation of a previously valid BIDS URI. For
example, a future version may specify an authority that would allow BIDS URIs to be resolved without reference to a localdataset_description.json.

### Units.

All units SHOULD be specified as perInternational System of Units(abbreviated as SI, from the French Système international (d’unités)) and can be SI units orSI derived
units. IncasetherearevalidreasonstodeviatefromSIunitsorSIderivedunits,theunitsMUSTbespecifiedinthesidecarJSONfile. IncasedataisexpressedinSIunitsor
SIderivedunits,theunitsMAYbespecifiedinthesidecarJSONfile. Incasenon-standardprefixesareaddedtoSIornon-SIunits,thesenon-standardprefixedunitsMUST
be specified in the JSON file. See the Units Appendix for a list of standard units and prefixes. Note also that for the formatting of SI units, theCMIXF-12convention for
encodingunitsisRECOMMENDED.CMIXFprovidesaconsistentsystemforallunitsandprefixsymbolswithonlybasiccharacters,avoidingsymbolsthatcancausetext
encoding problems; for example the CMIXF formatting for ”micro volts” isuV, ”degrees Celsius” isoCand ”Ohm” isOhm. See the Units Appendix for more information.

For additional rules, see below:

- Elapsed time SHOULD be expressed in seconds. Please note that some DICOM parameters have been traditionally expressed in milliseconds. Those need to be
    converted to seconds.
- Frequency SHOULD be expressed in Hertz.
- Arbitrary units SHOULD be indicated with the string"arbitrary".

Describing dates and timestamps:

- Date time information MUST be expressed in the following formatYYYY-MM-DDThh:mm:ss[.000000][Z](year, month, day, hour (24h), minute, second, optional
    fractional seconds, and optional UTC time indicator). This is almost equivalent to theRFC3339”date-time” format, with the exception that UTC indicatorZis
    optionalandnon-zeroUTCoffsetsarenotindicated. IfZisnotindicated,timezoneisalwaysassumedtobethelocaltimeofthedatasetviewer. Nospecificprecision
    is required for fractional seconds, but the precision SHOULD be consistent across the dataset. For example2009-06-15T13:45:30.
- Time stamp information MUST be expressed in the following format:hh:mm:ss[.000000]For example13:45:30.


- Notethat,dependingonlocalethicsboardpolicy,datetimeinformationmaynotneedtobefullydetailed. Forexample,itispermissibletosetthetimeto00:00:00
    if reporting the exact recording time is undesirable. However, for privacy protection reasons, it is RECOMMENDED to shift dates, as described below, without
    completely removing time information, as time information can be useful for research purposes.
- Dates can be shifted by a random number of days for privacy protection reasons. To distinguish real dates from shifted dates, is is RECOMMENDED to set shifted
    datestotheyear1925orearlier. Notethatsomedataformatsdonotsupportarbitraryrecordingdates. Forexample,theEDFdataformatcanonlycontainrecording
    datesafter1985. ForlongitudinalstudiesdatesMUSTbeshiftedbythesamenumberofdayswithineachsubjecttomaintaintheintervalinformation. Forexample:
    1867-06-15T13:45:30
- WARNING:TheNeuromag/Elekta/MEGINfileformatforMEG(.fif)doesnotsupportrecordingdatesearlierthan 1902 roughly. Someanalysissoftwarepackages
    (for example, MNE-Python) handle their data as.fifinternally and will break if recording dates are specified prior to 1902 , even if the original data format is not
    .fif. See the MEG File Formats Appendix for more information.
- AgeSHOULDbegivenasthenumberofyearssincebirthatthetimeofscanning(orfirstscanincaseofmultisessiondatasets). Usinghigheraccuracy(weeks)should
    in general be avoided due to privacy protection, unless when appropriate given the study goals, for example, when scanning babies.

### Directory structure.

#### Single session example.

This is an example of the directory and file structure. Because there is only one session, the session level is not required by the format. For details on individual files see
descriptions in the next section:

```
sub-control01/
anat/
sub-control01_T1w.nii.gz
sub-control01_T1w.json
sub-control01_T2w.nii.gz
sub-control01_T2w.json
func/
sub-control01_task-nback_bold.nii.gz
sub-control01_task-nback_bold.json
sub-control01_task-nback_events.tsv
sub-control01_task-nback_physio.tsv.gz
sub-control01_task-nback_physio.json
sub-control01_task-nback_sbref.nii.gz
dwi/
sub-control01_dwi.nii.gz
sub-control01_dwi.bval
sub-control01_dwi.bvec
fmap/
sub-control01_phasediff.nii.gz
```

```
sub-control01_phasediff.json
sub-control01_magnitude1.nii.gz
code/
deface.py
derivatives/
README
participants.tsv
dataset_description.json
CHANGES
```
### Unspecified data

Additional files and directories containing raw data MAY be added as needed for special cases. All non-standard file entities SHOULD conform to BIDS-style naming
conventions,includingalphabeticentitiesandsuffixesandalphanumericlabels/indices. Non-standardsuffixesSHOULDreflectthenatureofthedata,andexistingentities
SHOULD be used when appropriate. For example, an ASSET calibration scan might be namedsub-01_acq-ASSET_calibration.nii.gz.

Non-standard files and directories should be named with care. Future BIDS efforts may standardize new entities and suffixes, changing the meaning of filenames and
setting requirements on their contents or metadata. Validation and parsing tools MAY treat the presence of non-standard files and directories as an error, so consult the
details of these tools for mechanisms to suppress warnings or provide interpretations of your filenames.


## Modality agnostic files

### Dataset description.

Templates:

- dataset_description.json
- README
- CHANGES
- LICENSE

#### dataset_description.json

The filedataset_description.jsonis a JSON file describing the dataset. Every dataset MUST include this file with the following fields:

Key name Requirement Level Data type Description

Name REQUIRED string Name of the dataset.
BIDSVersion REQUIRED string The version of the BIDS standard that
was used.
HEDVersion RECOMMENDED stringorarrayofstrings If HED tags are used: The version of the
HED schema used to validate HED tags
for study. May include a single schema
or a base schema and one or more
library schema.


Key name Requirement Level Data type Description

DatasetLinks REQUIRED if [BIDS URIs][] are used objectofstrings Used to map a given<dataset-name>
from a DatasetLinks of the form
bids:<dataset-name>:path/within/dataset
to a local or remote location. The
<dataset-name>:""(an empty string)
is a reserved keyword that MUST NOT
be a key inDatasetLinks(example:
bids::path/within/dataset).
DatasetType RECOMMENDED string The interpretation of the dataset. For
backwards compatibility, the default
value is"raw". Must be one of:"raw",
"derivative".
License RECOMMENDED string The license for the dataset. The use of
license name abbreviations is
RECOMMENDED for specifying a
license (see License). The corresponding
full license text MAY be specified in an
additionalLICENSEfile.
Authors RECOMMENDED arrayofstrings List of individuals who contributed to
the creation/curation of the dataset.
Acknowledgements OPTIONAL string Text acknowledging contributions of
individuals or institutions beyond those
listed in Authors or Funding.
HowToAcknowledge OPTIONAL string Text containing instructions on how
researchers using this dataset should
acknowledge the original authors. This
field can also be used to define a
publication that should be cited in
publications that use the dataset.
Funding OPTIONAL arrayofstrings List of sources of funding (grant
numbers).
EthicsApprovals OPTIONAL arrayofstrings List of ethics committee approvals of
the research protocols and/or protocol
identifiers.
ReferencesAndLinks OPTIONAL arrayofstrings List of references to publications that
contain information on the dataset. A
reference may be textual or a
ReferencesAndLinks.


Key name Requirement Level Data type Description

DatasetDOI OPTIONAL string The Digital Object Identifier of the
dataset (not the corresponding paper).
DOIs SHOULD be expressed as a valid
DatasetDOI; bare DOIs such as
10.0.2.3/dfjj.10are DatasetDOI.
GeneratedBy RECOMMENDED arrayofobjects Used to specify provenance of the
dataset.
SourceDatasets RECOMMENDED arrayofobjects Used to specify the locations and
relevant attributes of all source
datasets. Valid keys in each object
include"URL","DOI"(see
SourceDatasets), and"Version"with
stringvalues.

Each object in theGeneratedByarray includes the following REQUIRED, RECOMMENDED and OPTIONAL keys:

Key name Requirement level Data type Description

Name REQUIRED string Name of the pipeline or process that
generated the outputs. Use"Manual"to
indicate the derivatives were generated
by hand, or adjusted manually after an
initial run of an automated pipeline.
Version RECOMMENDED string Version of the pipeline.
Description OPTIONAL string Plain-text description of the pipeline or
process that generated the outputs.
RECOMMENDED ifNameis"Manual".
CodeURL OPTIONAL string URL where the code used to generate
the dataset may be found.
Container OPTIONAL object Used to specify the location and
relevant attributes of software
container image used to produce the
dataset. Valid keys in this object
includeType,TagandURIwithstring
values.

Example:


##### {

```
"Name":"The mother of all experiments",
"BIDSVersion": "1.6.0",
"DatasetType": "raw",
"License":"CC0",
"Authors":[
"Paul Broca",
"Carl Wernicke"
],
"Acknowledgements":"Special thanks to Korbinian Brodmann for help in formatting this dataset in BIDS. We thank Alan Lloyd Hodgkin and Andrew Huxley for helpful comments and discussions about the experiment and manuscript; Hermann Ludwig Helmholtz for administrative support; and Claudius Galenus for providing data for the medial-to-lateral index analysis.",
"HowToAcknowledge":"Please cite this paper: https://www.ncbi.nlm.nih.gov/pubmed/001012092119281",
"Funding":[
"National Institute of Neuroscience Grant F378236MFH1",
"National Institute of Neuroscience Grant 5RMZ0023106"
],
"EthicsApprovals": [
"Army Human Research Protections Office (Protocol ARL-20098-10051, ARL 12-040, and ARL 12-041)"
],
"ReferencesAndLinks": [
"https://www.ncbi.nlm.nih.gov/pubmed/001012092119281",
"Alzheimer A., & Kraepelin, E. (2015). Neural correlates of presenile dementia in humans. Journal of Neuroscientific Data, 2, 234001. doi:1920.8/jndata.2015.7"
],
"DatasetDOI": "doi:10.0.2.3/dfjj.10",
"HEDVersion": "8.0.0",
"GeneratedBy": [
{
"Name":"reproin",
"Version": "0.6.0",
"Container":{
"Type": "docker",
"Tag":"repronim/reproin:0.6.0"
}
}
],
"SourceDatasets": [
{
"URL":"s3://dicoms/studies/correlates",
"Version": "April 11 2011"
}
]
```

##### }

Derived dataset and pipeline description

AsforanyBIDSdataset,adataset_description.jsonfileMUSTbefoundatthetoplevelofeveryderiveddataset:<dataset>/derivatives/<pipeline_name>/dataset_description.json.

In contrast to raw BIDS datasets, derived BIDS datasets MUST include aGeneratedBykey:

Key name Requirement Level Data type Description

GeneratedBy REQUIRED arrayofobjects Used to specify provenance of the
dataset.

Ifa derived datasetis stored as asubdirectory of the rawdataset, then theNamefieldof the firstGeneratedByobjectMUST be asubstring of the deriveddataset directory
name. That is, in a directory<dataset>/derivatives/<pipeline>[-<variant>]/, the firstGeneratedByobject should have aNameof<pipeline>.

Example:

{
"Name":"FMRIPREP Outputs",
"BIDSVersion": "1.6.0",
"DatasetType": "derivative",
"GeneratedBy": [
{
"Name":"fmriprep",
"Version": "1.4.1",
"Container":{
"Type": "docker",
"Tag":"poldracklab/fmriprep:1.4.1"
}
},
{
"Name":"Manual",
"Description": "Re-added RepetitionTime metadata to bold.json files"
}
],
"SourceDatasets": [
{
"DOI":"doi:10.18112/openneuro.ds000114.v1.0.1",
"URL":"https://openneuro.org/datasets/ds000114/versions/1.0.1",
"Version": "1.0.1"
}


##### ]

##### }

#### README.

A REQUIRED text file,README, SHOULD describe the dataset in more detail. TheREADMEfile MUST be either in ASCII or UTF-8 encoding and MAY have one of the
extensions:.md(Markdown),.rst(reStructuredText), or.txt. A BIDS dataset MUST NOT contain more than oneREADMEfile (with or without extension) at its root
directory. BIDS does not make any recommendations with regards to theMarkdown flavorand does not validate the syntax of Markdown and reStructuredText. The
READMEfile SHOULD be structured such that its contents can be easily understood even if the used format is not rendered. A guideline for creating a goodREADMEfile can
be found in thebids-starter-kit.

#### CHANGES.

Versionhistoryofthedataset(describingchanges,updatesandcorrections)MAYbeprovidedintheformofaCHANGEStextfile. ThisfileMUSTfollowtheCPANChangelog
convention. TheCHANGESfile MUST be either in ASCII or UTF-8 encoding.

Example:

1.0.1 2015-08-27

- Fixed slice timing information.

1.0.0 2015-08-17

- Initial release.

#### LICENSE.

ALICENSEfile MAY be provided in addition to the short specification of the used license in thedataset_description.json "License"field. The"License"field and
LICENSEfile MUST correspond. TheLICENSEfile MUST be either in ASCII or UTF-8 encoding.

### Participants file.

Template:

participants.tsv
participants.json

The purpose of this RECOMMENDED file is to describe properties of participants such as age, sex, handedness, species and strain. If this file exists, it MUST contain
the columnparticipant_id, which MUST consist ofsub-<label>values identifying one row for each participant, followed by a list of optional columns describing
participants. Each participant MUST be described by one and only one row.

TheRECOMMENDEDspeciescolumnSHOULDbeabinomialspeciesnamefromtheNCBITaxonomy(forexampleshomo sapiens,mus musculus,rattus norvegicus).
For backwards compatibility, ifspeciesis absent, the participant is assumed to behomo sapiens.


Commonly used optional columns inparticipants.tsvfiles areage,sex,handedness,strain, andstrain_rrid. We RECOMMEND to make use of these columns, and
in case that you do use them, we RECOMMEND to use the following values for them:

Column name Requirement Level Data type Description

participant_id REQUIRED string A participant identifier of the form
sub-<label>, matching a participant
entity found in the dataset. There
MUST be exactly one row for each
participant. Values inparticipant_id
MUST be unique.This column must
appear first in the file.
species RECOMMENDED string Thespeciescolumn SHOULD be a
binomial species name from theNCBI
Taxonomy(for example,homo
sapiens,mus musculus,rattus
norvegicus). For backwards
compatibility, ifspeciesis absent, the
participant is assumed to behomo
sapiens. This column may appear
anywhere in the file.
age RECOMMENDED number Numeric value in years (float or integer
value). This column may appear
anywhere in the file.
sex RECOMMENDED string String value indicating phenotypical
sex, one of ”male”, ”female”,
”other”.For ”male”, use one of these
values:male,m,M,MALE,Male.For
”female”, use one of these values:
female,f,F,FEMALE,Female.For
”other”, use one of these values:other,
o,O,OTHER,Other. This column may
appear anywhere in the file.For a list of
valid values for this column, see the sex.


Column name Requirement Level Data type Description

handedness RECOMMENDED string String value indicating one of ”left”,
”right”, ”ambidextrous”.For ”left”, use
one of these values:left,l,L,LEFT,
Left.For ”right”, use one of these
values:right,r,R,RIGHT,Right.For
”ambidextrous”, use one of these values:
ambidextrous,a,A,AMBIDEXTROUS,
Ambidextrous. This column may
appear anywhere in the file.For a list of
valid values for this column, see the
handedness.
strain RECOMMENDED string For species different fromhomo
sapiens, string value indicating the
strain of the species, for example:
C57BL/6J. This column may appear
anywhere in the file.
strain_rrid RECOMMENDED string For species different fromhomo
sapiens, research resource identifier
(RRID) of the strain of the species, for
example:RRID:IMSR_JAX:000664. This
column may appear anywhere in the
file.
Additional Columns OPTIONAL n/a Additional columns are allowed.

Throughout BIDS you can indicate missing values withn/a(for ”not available”).

participants.tsvexample:

participant_id age sex handedness group
sub-01 34 M right read
sub-02 12 F right write
sub-03 33 F n/a read

ItisRECOMMENDEDtoaccompanyeachparticipants.tsvfilewithasidecarparticipants.jsonfiletodescribetheTSVcolumnnamesandpropertiesoftheirvalues
(see also the section on tabular files). Such sidecar files are needed to interpret the data, especially so when optional columns are defined beyondage,sex,handedness,
species,strain,andstrain_rrid,suchasgroupinthisexample,orwhenadifferentageunitisneeded(forexample,gestationalweeks). Ifnounitsisprovidedforage,
it will be assumed to be in years relative to date of birth.

participants.jsonexample:


##### {

"age": {
"Description":"age of the participant",
"Units": "years"
},
"sex": {
"Description":"sex of the participant as reported by the participant",
"Levels":{
"M": "male",
"F": "female"
}
},
"handedness":{
"Description":"handedness of the participant as reported by the participant",
"Levels":{
"left": "left",
"right": "right"
}
},
"group":{
"Description":"experimental group the participant belonged to",
"Levels":{
"read": "participants who read an inspirational text before the experiment",
"write": "participants who wrote an inspirational text before the experiment"
}
}
}

### Samples file

Template:

samples.tsv
samples.json

The purpose of this file is to describe properties of samples, indicated by thesampleentity. This file is REQUIRED ifsample-<label>is present in any filename within
the dataset. Each sample MUST be described by one and only one row.


Column name Requirement Level Data type Description

sample_id REQUIRED string A sample identifier of the form
sample-<label>, matching a sample
entity found in the dataset. The
combination ofsample_idand
participant_idMUST be unique.
participant_id REQUIRED string A participant identifier of the form
sub-<label>, matching a participant
entity found in the dataset. The
combination ofsample_idand
participant_idMUST be unique.
sample_type REQUIRED string Biosample type defined byENCODE
Biosample Type. Must be one of:"cell
line","in vitro differentiated
cells","primary cell","cell-free
sample","cloning host","tissue",
"whole organisms","organoid",
"technical sample".
pathology RECOMMENDED string String value describing the pathology of
the sample or type of control. When
different fromhealthy, pathology
SHOULD be specified. The pathology
may be specified in eithersamples.tsv
orsessions.tsv, depending on
whether the pathology changes over
time.
derived_from RECOMMENDED string sample-<label>entity from which a
sample is derived, for example a slice of
tissue (sample-02) derived from a block
of tissue (sample-01).
Additional Columns OPTIONAL n/a Additional columns are allowed.

samples.tsvexample:

sample_id participant_id sample_type derived_from
sample-01 sub-01 tissue n/a
sample-02 sub-01 tissue sample-01
sample-03 sub-01 tissue sample-01
sample-04 sub-02 tissue n/a
sample-05 sub-02 tissue n/a


It is RECOMMENDED to accompany eachsamples.tsvfile with a sidecarsamples.jsonfile to describe the TSV column names and properties of their values (see also
the section on tabular files).

samples.jsonexample:

{
"sample_type":{
"Description":"type of sample from ENCODE Biosample Type (https://www.encodeproject.org/profiles/biosample_type)",
},
"derived_from": {
"Description":"sample_id from which the sample is derived"
}
}

### Phenotypic and assessment data

Template:

phenotype/
<measurement_tool_name>.tsv
<measurement_tool_name>.json

Optional: Yes

Ifthedatasetincludesmultiplesetsofparticipantlevelmeasurements(forexampleresponsesfrommultiplequestionnaires)theycanbesplitintoindividualfilesseparate
fromparticipants.tsv.

EachofthemeasurementfilesMUSTbekeptina/phenotypedirectoryplacedattherootoftheBIDSdatasetandMUSTendwiththe.tsvextension. FilenamesSHOULD
be chosen to reflect the contents of the file. For example, the ”Adult ADHD Clinical Diagnostic Scale” could be saved in a file called/phenotype/acds_adult.tsv.

The files can include an arbitrary set of columns, but one of them MUST beparticipant_idand the entries of that column MUST correspond to the subjects in the BIDS
dataset andparticipants.tsvfile.

As with all other tabular data, the additional phenotypic information files MAY be accompanied by a JSON file describing the columns in detail (see Tabular files).

In addition to the column descriptions, the JSON file MAY contain the following fields:


Key name Requirement Level Data type Description

MeasurementToolMetadata OPTIONAL object A description of the measurement tool
as a whole. Contains two fields:
"Description"and"TermURL".
"Description"is a free text
description of the measurement tool.
"TermURL"is a URL to an entity in an
ontology corresponding to this tool.
Derivative OPTIONAL boolean Indicates that values in the
corresponding column are
transformations of values from other
columns (for example a summary score
based on a subset of items in a
questionnaire). Must be one of:"true",
"false".

As an example, consider the contents of a file calledphenotype/acds_adult.json:

{
"MeasurementToolMetadata": {
"Description":"Adult ADHD Clinical Diagnostic Scale V1.2",
"TermURL":"https://www.cognitiveatlas.org/task/id/trm_5586ff878155d"
},
"adhd_b": {
"Description":"B. CHILDHOOD ONSET OF ADHD (PRIOR TO AGE 7)",
"Levels":{
"1": "YES",
"2": "NO"
}
},
"adhd_c_dx":{
"Description":"As child met A, B, C, D, E and F diagnostic criteria",
"Levels":{
"1": "YES",
"2": "NO"
}
}
}

Please note that in this exampleMeasurementToolMetadataincludes information about the questionnaire andadhd_bandadhd_c_dxcorrespond to individual columns.


In addition to the keys available to describe columns in all tabular files (LongName,Description,Levels,Units, andTermURL) theparticipants.jsonfile as well as
phenotypicfilescanalsoincludecolumndescriptionswithaDerivativefieldthat,whensettotrue,indicatesthatvaluesinthecorrespondingcolumnisatransformation
of values from other columns (for example a summary score based on a subset of items in a questionnaire).

### Scans file

Template:

sub-<label>/
[ses-<label>/]
sub-<label>[_ses-<label>]_scans.tsv
sub-<label>[_ses-<label>]_scans.json

Optional: Yes

The purpose of this file is to describe timing and other properties of each neural recording file within one session. In general, each of these files SHOULD be described by
exactly one row.

For file formats that are based on several files of different extensions, or a directory of files with different extensions (multi-file file formats), only that file SHOULD be
listed that would also be passed to analysis software for reading the data. For example for BrainVision data (.vhdr,.vmrk,.eeg), only the.vhdrSHOULD be listed; for
EEGLAB data (.set,.fdt), only the.setfile SHOULD be listed; and for CTF data (.ds), the whole.dsdirectory SHOULD be listed, and not the individual files in that
directory.

Some neural recordings consist of multiple parts, that span several files, but that share the same extension. For example in entity-linked file collections, commonly used
for qMRI, where recordings may be linked through entities such asechoandpart(using.niior.nii.gzextensions). For another example consider the case of large
files in.fifformat that are linked through thesplitentity (see Split files). Such recordings MUST be documented with one row per file (unlike the case of multi-file file
formats described above).

Column name Requirement Level Data type Description

filename REQUIRED string Relative paths to files. There MUST be
exactly one row for each file. Values in
filenameMUST be unique.This column
must appear first in the file.
acq_time OPTIONAL string Acquisition time refers to when the first
data point in each run was acquired.
Furthermore, if this header is provided,
the acquisition times of all files from the
same recording MUST be identical.
Datetime format and their
anonymization are described in
acq_time. This column may appear
anywhere in the file.


Column name Requirement Level Data type Description

Additional Columns OPTIONAL n/a Additional columns are allowed.

Additionalfieldscanincludeexternalbehavioralmeasuresrelevanttothescan. Forexamplevigilancequestionnairescoreadministeredafterarestingstatescan. Allsuch
included additional fields SHOULD be documented in an accompanying_scans.jsonfile that describes these fields in detail (see Tabular files).

Example_scans.tsv:

filename acq_time
func/sub-control01_task-nback_bold.nii.gz 1877-06-15T13:45:30
func/sub-control01_task-motor_bold.nii.gz 1877-06-15T13:55:33
meg/sub-control01_task-rest_split-01_meg.nii.gz 1877-06-15T12:15:27
meg/sub-control01_task-rest_split-02_meg.nii.gz 1877-06-15T12:15:27

### Sessions file

Template:

sub-<label>/
sub-<label>_sessions.tsv

Optional: Yes

Incaseofmultiplesessionsthereisanoptionofaddingadditionalsessions.tsvfilesdescribingvariableschangingbetweensessions. Insuchcaseonefileperparticipant
SHOULD be added. These files MUST include asession_idcolumn and describe each session by one and only one row. Column names insessions.tsvfiles MUST be
different from group level participant key column names in theparticipants.tsvfile.

Column name Requirement Level Data type Description

session_id REQUIRED string A session identifier of the form
ses-<label>, matching a session found
in the dataset. There MUST be exactly
one row for each session. Values in
session_idMUST be unique.This
column must appear first in the file.
acq_time OPTIONAL string Acquisition time refers to when the first
data point of the first run was acquired.
Datetime format and their
anonymization are described in
acq_time. This column may appear
anywhere in the file.


Column name Requirement Level Data type Description

pathology RECOMMENDED string String value describing the pathology of
the sample or type of control. When
different fromhealthy, pathology
SHOULD be specified. The pathology
may be specified in eithersamples.tsv
orsessions.tsv, depending on
whether the pathology changes over
time. This column may appear
anywhere in the file.
Additional Columns OPTIONAL n/a Additional columns are allowed.

_sessions.tsvexample:

session_id acq_time systolic_blood_pressure
ses-predrug 2009-06-15T13:45:30 120
ses-postdrug 2009-06-16T13:45:30 100
ses-followup 2009-06-17T13:45:30 110

### Code.

Template:code/*

Source code of scripts that were used to prepare the dataset MAY be stored here. Examples include anonymization or defacing of the data, or the conversion from
the format of the source data to the BIDS format (see source vs. raw vs. derived data). Extra care should be taken to avoid including original IDs or any identifiable
information with the source code. There are no limitations or recommendations on the language and/or code organization of these scripts at the moment.


## Magnetic Resonance Imaging

### Common metadata fields

MR Data described in the following sections share the following RECOMMENDED metadata fields (stored in sidecar JSON files). MRI acquisition parameters are divided
into several categories based on ”A checklist for fMRI acquisition methods reporting in the literature” (article,checklist) by Ben Inglis.

#### Scanner Hardware

Key name Requirement Level Data type Description

Manufacturer RECOMMENDED string Manufacturer of the equipment that
produced the measurements.
Corresponds to DICOM Tag 0008, 0070
Manufacturer.
ManufacturersModelName RECOMMENDED string Manufacturer’s model name of the
equipment that produced the
measurements. Corresponds to DICOM
Tag 0008, 1090Manufacturers Model
Name.
DeviceSerialNumber RECOMMENDED string The serial number of the equipment
that produced the measurements. A
pseudonym can also be used to prevent
the equipment from being identifiable,
so long as each pseudonym is unique
within the dataset. Corresponds to
DICOM Tag 0018, 1000
DeviceSerialNumber.


Key name Requirement Level Data type Description

StationName RECOMMENDED string Institution defined name of the machine
that produced the measurements.
Corresponds to DICOM Tag 0008, 1010
Station Name.
SoftwareVersions RECOMMENDED string Manufacturer’s designation of software
version of the equipment that produced
the measurements. Corresponds to
DICOM Tag 0018, 1020Software
Versions.
HardcopyDeviceSoftwareVersion HardcopyDeviceSoftwareVersion string Manufacturer’s designation of the
software of the device that created this
Hardcopy Image (the printer).
Corresponds to DICOM Tag 0018, 101A
Hardcopy Device Software Version.
MagneticFieldStrength RECOMMENDED, but REQUIRED for
Arterial Spin Labeling

number Nominal field strength of MR magnet in
Tesla. Corresponds to DICOM Tag 0018,
0087 Magnetic Field Strength.
ReceiveCoilName RECOMMENDED string Information describing the receiver coil.
Corresponds to DICOM Tag 0018, 1250
Receive Coil Name, although not all
vendors populate that DICOM Tag, in
whichcasethisfieldcanbederivedfrom
an appropriate private DICOM field.
ReceiveCoilActiveElements RECOMMENDED string Information describing the
active/selected elements of the receiver
coil. This does not correspond to a tag
in the DICOM ontology. The
vendor-defined terminology for active
coil elements can go in this field.
GradientSetType RECOMMENDED string It should be possible to infer the
gradient coil from the scanner model. If
not, for example because of a custom
upgrade or use of a gradient insert set,
then the specifications of the actual
gradient coil should be reported
independently.


```
Key name Requirement Level Data type Description
MRTransmitCoilSequence RECOMMENDED string This is a relevant field if a non-standard
transmit coil is used. Corresponds to
DICOM Tag 0018, 9049MR Transmit
Coil Sequence.
MatrixCoilMode RECOMMENDED string (If used) A method for reducing the
number of independent channels by
combining in analog the signals from
multiple coil elements. There are
typically different default modes when
using un-accelerated or accelerated (for
example,"GRAPPA","SENSE") imaging.
CoilCombinationMethod RECOMMENDED string Almost all fMRI studies using
phased-array coils use
root-sum-of-squares (rSOS)
combination, but other methods exist.
The image reconstruction is changed by
the coil combination method (as for the
matrix coil mode above), so anything
non-standard should be reported.
```
Example forReceiveCoilActiveElements:
ForSiemens,coilchannelsaretypicallynotactivated/selectedindividually,butratherinpre-definedselectable”groups”ofindividualchannels,andthelistofthe”groups”
of elements that are active/selected in any given scan populates theCoil Stringentry in Siemens’ private DICOM fields (for example,HEA;HEPfor the Siemens standard
32 ch coil when both the anterior and posterior groups are activated). This is a flexible field that can be used as most appropriate for a given vendor and coil to define the
”active” coil elements. Since individual scans can sometimes not have the intended coil elements selected, it is preferable for this field to be populated directly from the
DICOM for each individual scan, so that it can be used as a mechanism for checking that a given scan was collected with the intended coil elements selected.

#### Sequence Specifics

```
Key name Requirement Level Data type Description
PulseSequenceType RECOMMENDED string A general description of the pulse
sequence used for the scan (for example,
"MPRAGE","Gradient Echo EPI",
"Spin Echo EPI","Multiband
gradient echo EPI").
```

Key name Requirement Level Data type Description

ScanningSequence RECOMMENDED stringorarrayofstrings Description of the type of data acquired.
Corresponds to DICOM Tag 0018, 0020
Scanning Sequence.
SequenceVariant RECOMMENDED stringorarrayofstrings Variant of the ScanningSequence.
Corresponds to DICOM Tag 0018, 0021
Sequence Variant.
ScanOptions RECOMMENDED stringorarrayofstrings Parameters of ScanningSequence.
Corresponds to DICOM Tag 0018, 0022
Scan Options.
SequenceName RECOMMENDED string Manufacturer’s designation of the
sequence name. Corresponds to DICOM
Tag 0018, 0024Sequence Name.
PulseSequenceDetails RECOMMENDED string Information beyond pulse sequence
type that identifies the specific pulse
sequence used (for example,"Standard
Siemens Sequence distributed with
the VB17 software","Siemens WIP
### version #.##,"or"Sequence
written by X using a version
compiled on MM/DD/YYYY").
NonlinearGradientCorrection RECOMMENDED, but REQUIRED if
NonlinearGradientCorrection data are
present

boolean Boolean stating if the image saved has
been corrected for gradient
nonlinearities by the scanner sequence.
Must be one of:"true","false".
MRAcquisitionType RECOMMENDED, but REQUIRED for
Arterial Spin Labeling

string Type of sequence readout. Corresponds
to DICOM Tag 0018, 0023MR
Acquisition Type. Must be one of:
"2D","3D".
MTState RECOMMENDED boolean Boolean stating whether the
magnetization transfer pulse is applied.
Corresponds to DICOM Tag 0018, 9020
Magnetization Transfer. Must be one
of:"true","false".
MTOffsetFrequency OPTIONAL number The frequency offset of the
magnetization transfer pulse with
respect to the central H1 Larmor
frequency in Hertz (Hz).


Key name Requirement Level Data type Description

MTPulseBandwidth OPTIONAL number The excitation bandwidth of the
magnetization transfer pulse in Hertz
(Hz).
MTNumberOfPulses OPTIONAL number The number of magnetization transfer
RF pulses applied before the readout.
MTPulseShape OPTIONAL string Shape of the magnetization transfer RF
pulse waveform. The value
"GAUSSHANN"refers to a Gaussian pulse
with a Hanning window. The value
"SINCHANN"refers to a sinc pulse with a
Hanning window. The value
"SINCGAUSS"refers to a sinc pulse with
a Gaussian window. Must be one of:
"HARD","GAUSSIAN","GAUSSHANN",
"SINC","SINCHANN","SINCGAUSS",
"FERMI".
MTPulseDuration OPTIONAL number Duration of the magnetization transfer
RF pulse in seconds.
SpoilingState RECOMMENDED boolean Boolean stating whether the pulse
sequence uses any type of spoiling
strategy to suppress residual transverse
magnetization. Must be one of:"true",
"false".
SpoilingType OPTIONAL string Specifies which spoiling method(s) are
used by a spoiled sequence. Must be one
of:"RF","GRADIENT","COMBINED".
SpoilingRFPhaseIncrement OPTIONAL number The amount of incrementation
described in degrees, which is applied to
the phase of the excitation pulse at each
TR period for achieving RF spoiling.
SpoilingGradientMoment OPTIONAL number Zeroth moment of the spoiler gradient
lobe in millitesla times second per meter
(mT.s/m).
SpoilingGradientDuration OPTIONAL number The duration of the spoiler gradient
lobe in seconds. The duration of a
trapezoidal lobe is defined as the
summation of ramp-up and plateau
times.


#### In-Plane Spatial Encoding.

Key name Requirement Level Data type Description

NumberShots RECOMMENDED numberorarrayofnumbers The number of RF excitations needed
to reconstruct a slice or volume (may be
referred to as partition). Please mind
that this is not the same as Echo Train
Length which denotes the number of
k-space lines collected after excitation
in a multi-echo readout. The data type
array is applicable for specifying this
parameter before and after the k-space
center is sampled. Please see
NumberShots in the qMRI appendix for
corresponding calculations.
ParallelReductionFactorInPlane RECOMMENDED number The parallel imaging (for instance,
GRAPPA) factor. Use the denominator
of the fraction of k-space encoded for
each slice. For example, 2 means half of
k-space is encoded. Corresponds to
DICOM Tag 0018, 9069Parallel
Reduction Factor In-plane.
ParallelAcquisitionTechnique RECOMMENDED string The type of parallel imaging used (for
example"GRAPPA","SENSE").
Corresponds to DICOM Tag 0018, 9078
Parallel Acquisition Technique.
PartialFourier RECOMMENDED number The fraction of partial Fourier
information collected. Corresponds to
DICOM Tag 0018, 9081Partial
Fourier.
PartialFourierDirection RECOMMENDED string The direction where only partial
Fourier information was collected.
Corresponds to DICOM Tag 0018, 9036
Partial Fourier Direction.


Key name Requirement Level Data type Description

EffectiveEchoSpacing RECOMMENDED, but REQUIRED if
corresponding fieldmap data present

number The ”effective” sampling interval,
specified in seconds, between lines in the
phase-encoding direction, defined based
on the size of the reconstructed image
in the phase direction. It is frequently,
but incorrectly, referred to as ”dwell
time” (see the"DwellTime"parameter
for actual dwell time). It is REQUIRED
for unwarping distortions using field
maps. Note that beyond just in-plane
acceleration, a variety of other
manipulations to the phase encoding
need to be accounted for properly,
including partial fourier, phase
oversampling, phase resolution, phase
field-of-view and interpolation. 2Must
be a number greater than 0.
MixingTime RECOMMENDED number In the context of a stimulated- and
spin-echo 3D EPI sequence for B1+
mapping, corresponds to the interval
between spin- and stimulated-echo
pulses. In the context of a
diffusion-weighted double spin-echo
sequence, corresponds to the interval
between two successive diffusion
sensitizing gradients, specified in
seconds.


Key name Requirement Level Data type Description

PhaseEncodingDirection RECOMMENDED, but REQUIRED if
corresponding fieldmap data is present
or when using multiple runs with
different phase encoding directions
(which can be later used for field
inhomogeneity correction).

string The lettersi,j,kcorrespond to the first,
second and third axis of the data in the
NIFTI file. The polarity of the phase
encoding is assumed to go from zero
index to maximum index unless-sign
is present (then the order is reversed -
starting from the highest index instead
of zero).PhaseEncodingDirectionis
defined as the direction along which
phase is was modulated which may
result in visible distortions. Note that
this is not the same as the DICOM term
InPlanePhaseEncodingDirection
which can haveROWorCOLvalues. Must
be one of:"i","j","k","i-","j-",
"k-".
TotalReadoutTime RECOMMENDED, but REQUIRED if
corresponding ’field/distortion’ maps
acquired with opposing phase encoding
directions are present (see
TotalReadoutTime)

```
number This is actually the ”effective” total
readout time, defined as the readout
duration, specified in seconds, that
would have generated data with the
given level of distortion. It is NOT the
actual, physical duration of the readout
train. If"EffectiveEchoSpacing"has
been properly computed, it is just
EffectiveEchoSpacing *
(ReconMatrixPE - 1).
```
2Conveniently, for Siemens data, this value is easily obtained as1 / (BWPPPE * ReconMatrixPE), where BWPPPE is the ”BandwidthPerPixelPhaseEncode” in DICOM
Tag 0019, 1028 and ReconMatrixPE is the size of the actual reconstructed data in the phase direction (which is NOT reflected in a single DICOM Tag for all possible
aforementioned scan manipulations). Seehereandhere

3We use the time between the center of the first ”effective” echo and the center of the last ”effective” echo, sometimes called the ”FSL definition”.

#### Timing Parameters.


Key name Requirement Level Data type Description

EchoTime RECOMMENDED, but REQUIRED if
corresponding fieldmap data is present,
or the data comes from a multi-echo
sequence or Arterial Spin Labeling.

numberorarrayofnumbers The echo time (TE) for the acquisition,
specified in seconds. Corresponds to
DICOM Tag 0018, 0081Echo Time
(please note that the DICOM term is in
milliseconds not seconds). The data
type number may apply to files from
any MRI modality concerned with a
single value for this field, or to the files
in a EchoTime where the value of this
field is iterated using the EchoTime.
The data type array provides a value
for each volume in a 4D dataset and
should only be used when the volume
timing is critical for interpretation of
the data, such as in EchoTime or
variable echo time fMRI sequences.
InversionTime RECOMMENDED number The inversion time (TI) for the
acquisition, specified in seconds.
Inversion time is the time after the
middle of inverting RF pulse to middle
of excitation pulse to detect the amount
of longitudinal magnetization.
Corresponds to DICOM Tag 0018, 0082
Inversion Time(please note that the
DICOM term is in milliseconds not
seconds). Must be a number greater
than 0.


Key name Requirement Level Data type Description

SliceTiming RECOMMENDED, but REQUIRED for
sparse sequences that do not have the
DelayTimefield set, and Arterial Spin
Labeling withMRAcquisitionTypeset
on2D.

```
arrayofnumbers The time at which each slice was
acquired within each volume (frame) of
the acquisition. Slice timing is not slice
order -- rather, it is a list of times
containing the time (in seconds) of each
slice acquisition in relation to the
beginning of volume acquisition. The
list goes through the slices along the
slice axis in the slice encoding
dimension (see below). Note that to
ensure the proper interpretation of the
"SliceTiming"field, it is important to
check if the OPTIONAL
SliceEncodingDirectionexists. In
particular, if
"SliceEncodingDirection"is
negative, the entries in"SliceTiming"
are defined in reverse order with respect
to the slice axis, such that the final
entry in the"SliceTiming"list is the
time of acquisition of slice 0. Without
this parameter slice time correction will
not be possible.
```

Key name Requirement Level Data type Description

SliceEncodingDirection RECOMMENDED string The axis of the NIfTI data along which
slices were acquired, and the direction
in which"SliceTiming"is defined with
respect to.i,j,kidentifiers correspond
to the first, second and third axis of the
data in the NIfTI file. A-sign indicates
that the contents of"SliceTiming"are
defined in reverse order - that is, the
first entry corresponds to the slice with
the largest index, and the final entry
corresponds to slice index zero. When
present, the axis defined by
"SliceEncodingDirection"needs to
be consistent with theslice_dimfield
in the NIfTI header. When absent, the
entries in"SliceTiming"must be in
the order of increasing slice index as
defined by the NIfTI header. Must be
one of:"i","j","k","i-","j-","k-".
DwellTime RECOMMENDED number Actual dwell time (in seconds) of the
receiver per point in the readout
direction, including any oversampling.
For Siemens, this corresponds to
DICOM field 0019, 1018 (in ns). This
value is necessary for the OPTIONAL
readout distortion correction of
anatomicals in the HCP Pipelines. It
also usefully provides a handle on the
readout bandwidth, which isn’t
captured in the other metadata tags.
Not to be confused with
"EffectiveEchoSpacing", and the
frequent mislabeling of echo spacing
(which is spacing in the phase encoding
direction) as ”dwell time” (which is
spacing in the readout direction).

#### RF & Contrast


Key name Requirement Level Data type Description

FlipAngle RECOMMENDED, but REQUIRED if
LookLocker is set totrue

numberorarrayofnumbers Flip angle (FA) for the acquisition,
specified in degrees. Corresponds to:
DICOM Tag 0018, 1314Flip Angle.
The data type number may apply to
files from any MRI modality concerned
with a single value for this field, or to
the files in a FlipAngle where the value
of this field is iterated using the
FlipAngle. The data type array
provides a value for each volume in a
4D dataset and should only be used
when the volume timing is critical for
interpretation of the data, such as in
FlipAngle or variable flip angle fMRI
sequences.
NegativeContrast OPTIONAL boolean trueorfalsevalue specifying whether
increasing voxel intensity (within
sample voxels) denotes a decreased
value with respect to the contrast suffix.
This is commonly the case when
Cerebral Blood Volume is estimated via
usage of a contrast agent in conjunction
with a T2* weighted acquisition
protocol. Must be one of:"true",
"false".

#### Slice Acceleration.

Key name Requirement Level Data type Description

MultibandAccelerationFactor RECOMMENDED number The multiband factor, for multiband
acquisitions.

#### Anatomical landmarks.

Useful for multimodal co-registration with MEG, (S)EEG, TMS, and so on.


Key name Requirement Level Data type Description

AnatomicalLandmarkCoordinates RECOMMENDED objectofarrays Key-value pairs of any number of
additional anatomical landmarks and
their coordinates in voxel units (where
first voxel has index 0,0,0) relative to
the associated anatomical MRI (for
example,{"AC": [127,119,149],
"PC": [128,93,141], "IH":
[131,114,206]}, or{"NAS":
[127,213,139], "LPA":
[52,113,96], "RPA":
[202,113,91]}). Each array MUST
contain three numeric values
corresponding to x, y, and z axis of the
coordinate system in that exact order.

#### Echo-Planar Imaging and B0 mapping.

Echo-Planar Imaging (EPI) schemes typically used in the acquisition of diffusion and functional MRI may also be intended for estimating the B0 field nonuniformity
inside the scanner (in other words, mapping the field) without the acquisition of additional MRI schemes such as gradient-recalled echo (GRE) sequences that are stored
under thefmap/directory of the BIDS structure.

The modality labelsdwi(underdwi/),bold(underfunc/),asl(underperf/),sbref(underdwi/,func/orperf/), and any modality underfmap/are allowed to encode
the MR protocol intent for fieldmap estimation using the following metadata:


Key name Requirement Level Data type Description

B0FieldIdentifier RECOMMENDED stringorarrayofstrings The presence of this key states that this
particular 3D or 4D image MAY be used
for fieldmap estimation purposes. Each
"B0FieldIdentifier"MUST be a
unique string within one participant’s
tree, shared only by the images meant
to be used as inputs for the estimation
of a particular instance of the B0 field
estimation. It is RECOMMENDED to
derive this identifier from DICOM Tags,
for example, DICOM tag 0018, 1030
Protocol Name, or DICOM tag 0018,
0024 Sequence Namewhen the former is
not defined (for example, in GE
devices.)
B0FieldSource RECOMMENDED stringorarrayofstrings At least one existing
"B0FieldIdentifier"defined by
images in the participant’s tree. This
field states the B0 field estimation
designated by the
"B0FieldIdentifier"that may be
used to correct the dataset for
distortions caused by B0
inhomogeneities."B0FieldSource"and
"B0FieldIdentifier"MAY both be
present for images that are used to
estimate their own B0 field, for
example, in ”pepolar” acquisitions.

#### Institution information

Key name Requirement Level Data type Description

InstitutionName RECOMMENDED string The name of the institution in charge of
the equipment that produced the
measurements. Corresponds to DICOM
Tag 0008, 0080InstitutionName.


```
Key name Requirement Level Data type Description
InstitutionAddress RECOMMENDED string The address of the institution in charge
of the equipment that produced the
measurements. Corresponds to DICOM
Tag 0008, 0081InstitutionAddress.
InstitutionalDepartmentName RECOMMENDED string The department in the institution in
charge of the equipment that produced
the measurements. Corresponds to
DICOM Tag 0008, 1040Institutional
Department Name.
```
When adding additional metadata please use the CamelCase version ofDICOM ontology termswhenever possible. See also recommendations on JSON files.

### Anatomy imaging data

```
Template:
sub-<label>/
[ses-<label>/]
anat/
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>][_part-<mag|phase|real|imag>]_<suffix>.json
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>][_part-<mag|phase|real|imag>]_<suffix>.nii[.gz]
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>]_<suffix>.json
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>]_<suffix>.nii[.gz]
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>][_mod-<label>]_defacemask.json
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>][_mod-<label>]_defacemask.nii[.gz]
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>]_echo-<index>[_part-<mag|phase|real|imag>]_MEGRE.json
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>]_echo-<index>[_part-<mag|phase|real|imag>]_MEGRE.nii[.gz]
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>]_echo-<index>[_part-<mag|phase|real|imag>]_MESE.json
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>]_echo-<index>[_part-<mag|phase|real|imag>]_MESE.nii[.gz]
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>][_echo-<index>]_flip-<index>[_part-<mag|phase|real|imag>]_VFA.json
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>][_echo-<index>]_flip-<index>[_part-<mag|phase|real|imag>]_VFA.nii[.gz]
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>]_inv-<index>[_part-<mag|phase|real|imag>]_IRT1.json
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>]_inv-<index>[_part-<mag|phase|real|imag>]_IRT1.nii[.gz]
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>][_echo-<index>][_flip-<index>]_inv-<index>[_part-<mag|phase|real|imag>]_MP2RAGE.json
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>][_echo-<index>][_flip-<index>]_inv-<index>[_part-<mag|phase|real|imag>]_MP2RAGE.nii[.gz]
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>][_echo-<index>]_flip-<index>_mt-<on|off>[_part-<mag|phase|real|imag>]_MPM.json
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>][_echo-<index>]_flip-<index>_mt-<on|off>[_part-<mag|phase|real|imag>]_MPM.nii[.gz]
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>][_echo-<index>]_flip-<index>_mt-<on|off>[_part-<mag|phase|real|imag>]_MTS.json
```

```
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>][_echo-<index>]_flip-<index>_mt-<on|off>[_part-<mag|phase|real|imag>]_MTS.nii[.gz]
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>]_mt-<on|off>[_part-<mag|phase|real|imag>]_MTR.json
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>]_mt-<on|off>[_part-<mag|phase|real|imag>]_MTR.nii[.gz]
```
Legend:

- Filename entities or directories between square brackets (for example,[_ses-<label>]) are OPTIONAL.
- Some entities may only allow specific values, in which case those values are listed in<>, separated by|.
- _<suffix>means that there are several (>6) valid suffixes for this filename pattern.
- .<extension>means that there are several (>6) valid extensions for this file type.
- [.gz]means that both the unzipped and gzipped versions of the extension are valid.

Currently supported non-parametric structural MR images include:

```
Name suffix Description
Fluid attenuated inversion recovery image FLAIR In arbitrary units (arbitrary). Structural images with
predominant T2 contribution (also known as
T2-FLAIR), in which signal from fluids (for example,
CSF) is nulled out by adjusting inversion time,
coupled with notably long repetition and echo times.
PD and T2 weighted image PDT2 In arbitrary units (arbitrary). PDw and T2w images
acquired using a dual echo FSE sequence through
view sharing process (Johnson et al. 1994).
Proton density (PD) weighted image PDw In arbitrary units (arbitrary). The contrast of these
images is mainly determined by spatial variations in
the spin density (1H) of the imaged specimen. In
spin-echo sequences this contrast is achieved at short
repetition and long echo times. In a gradient-echo
acquisition, PD weighting dominates the contrast at
long repetition and short echo times, and at small flip
angles.
```

Name suffix Description

T1-weighted image T1w In arbitrary units (arbitrary). The contrast of these
images is mainly determined by spatial variations in
the longitudinal relaxation time of the imaged
specimen. In spin-echo sequences this contrast is
achieved at relatively short repetition and echo times.
To achieve this weighting in gradient-echo images,
again, short repetition and echo times are selected;
however, at relatively large flip angles. Another
common approach to increase T1 weighting in
gradient-echo images is to add an inversion
preparation block to the beginning of the imaging
sequence (for example,TurboFLASHorMP-RAGE).
T2star weighted image T2starw In arbitrary units (arbitrary). The contrast of these
images is mainly determined by spatial variations in
the (observed) transverse relaxation time of the
imaged specimen. In spin-echo sequences, this effect
is negated as the excitation is followed by an
inversion pulse. The contrast of gradient-echo images
natively depends on T2-star effects. However, for
T2-star variation to dominate the image contrast,
gradient-echo acquisitions are carried out at long
repetition and echo times, and at small flip angles.
T2-weighted image T2w In arbitrary units (arbitrary). The contrast of these
images is mainly determined by spatial variations in
the (true) transverse relaxation time of the imaged
specimen. In spin-echo sequences this contrast is
achieved at relatively long repetition and echo times.
Generally, gradient echo sequences are not the most
suitable option for achieving T2 weighting, as their
contrast natively depends on T2-star rather than on
T2.
Homogeneous (flat) T1-weighted MP2RAGE image UNIT1 In arbitrary units (arbitrary). UNIT1 images are
REQUIRED to use this suffix regardless of the
method used to generate them. Note that although
this image is T1-weighted, regions without MR signal
will contain white salt-and-pepper noise that most
segmentation algorithms will fail on. Therefore, it is
important to dissociate it fromT1w. Please see UNIT1
in the qMRI appendix for further information.


```
Name suffix Description
Angiogram angio Magnetic resonance angiography sequences focus on
enhancing the contrast of blood vessels (generally
arteries, but sometimes veins) against other tissue
types.
Inplane T1 inplaneT1 In arbitrary units (arbitrary). T1 weighted structural
image matched to a functional (task) image.
Inplane T2 inplaneT2 In arbitrary units (arbitrary). T2 weighted structural
image matched to a functional (task) image.
```
If the structural images included in the dataset were defaced (to protect identity of participants) one MAY provide the binary mask that was used to remove facial
features in the form of_defacemaskfiles. In such cases, the OPTIONALmod-<label>entity corresponds to modality suffix, such asT1worinplaneT1, referenced by the
defacemask image. For example,sub-01_mod-T1w_defacemask.nii.gz.

SomemetainformationabouttheacquisitionMAYbeprovidedinanadditionalJSONfile. SeeCommonmetadatafieldsforalistoftermsandtheirdefinitions. Thereare
also some OPTIONAL JSON fields specific to anatomical scans:

Key name Requirement Level Data type Description

ContrastBolusIngredient OPTIONAL string Active ingredient of agent. Corresponds
to DICOM Tag 0018, 1048
Contrast/Bolus Ingredient. Must be
one of:"IODINE","GADOLINIUM",
"CARBON DIOXIDE","BARIUM","XENON".
RepetitionTimeExcitation OPTIONAL number The interval, in seconds, between two
successive excitations.DICOM Tag
0018, 0080best refers to this parameter.
This field may be used together with the
"RepetitionTimePreparation"for
certain use cases, such asMP2RAGE.
UseRepetitionTimeExcitation(in
combination with
"RepetitionTimePreparation"if
needed) for anatomy imaging data
rather than"RepetitionTime"as it is
already defined as the amount of time
that it takes to acquire a single volume
in the RepetitionTimeExcitation
section. Must be a number greater than
or equal to 0.


```
Key name Requirement Level Data type Description
RepetitionTimePreparation OPTIONAL numberorarrayofnumbers The interval, in seconds, that it takes a
preparation pulse block to re-appear at
the beginning of the succeeding
(essentially identical) pulse sequence
block. The data type number may
apply to files from any MRI modality
concerned with a single value for this
field. The data type array provides a
value for each volume in a 4D dataset
and should only be used when the
volume timing is critical for
interpretation of the data, such as in
RepetitionTimePreparation.
```
```
Thepart-<label>entity is used to indicate which component of the complex representation of the MRI signal is represented in voxel data. This entity is associated with
theDICOMTag0008, 9208. Allowedlabelvaluesforthisentityarephase,mag,realandimag,whicharetypicallyusedinpart-mag/part-phaseorpart-real/part-imag
pairs of files. For example:
sub-01/
anat/
sub-01_part-mag_T1w.nii.gz
sub-01_part-mag_T1w.json
sub-01_part-phase_T1w.nii.gz
sub-01_part-phase_T1w.json
Phase images MAY be in radians or in arbitrary units. The sidecar JSON file MUST include the units of thephaseimage. The possible options areradorarbitrary.
For example, forsub-01_part-phase_T1w.json:
{
"Units": "rad"
}
```
When there is only a magnitude image of a given type, thepartentity MAY be omitted.

```
Similarly, the OPTIONALrec-<label>entity can be used to distinguish different reconstruction algorithms (for example ones using motion correction).
Structural MR images whose intensity is represented in a non-arbitrary scale constitute parametric maps. Currently supported parametric maps include:
```

Name suffix Description

Quantitative susceptibility map (QSM) Chimap In parts per million (ppm). QSM allows for
determining the underlying magnetic susceptibility
of tissue (Chi) (Wang & Liu, 2014). Chi maps are
REQUIRED to use this suffix regardless of the
method used to generate them.
Equilibrium magnetization (M0) map M0map In arbitrary units (arbitrary). A common
quantitative MRI (qMRI) fitting variable that
represents the amount of magnetization at thermal
equilibrium. M0 maps are RECOMMENDED to use
this suffix if generated by qMRI applications (for
example, variable flip angle T1 mapping).
Magnetization transfer ratio image MTRmap In arbitrary units (arbitrary). MTR maps are
REQUIRED to use this suffix regardless of the
method used to generate them. MTRmap intensity
values are RECOMMENDED to be represented in
percentage in the range of 0-100%.
Macromolecular tissue volume (MTV) image MTVmap In arbitrary units (arbitrary). MTV maps are
REQUIRED to use this suffix regardless of the
method used to generate them.
Magnetization transfer saturation image MTsat In arbitrary units (arbitrary). MTsat maps are
REQUIRED to use this suffix regardless of the
method used to generate them.
Myelin water fraction image MWFmap In arbitrary units (arbitrary). MWF maps are
REQUIRED to use this suffix regardless of the
method used to generate them. MWF intensity values
are RECOMMENDED to be represented in percentage
in the range of 0-100%.
Combined PD/T2 image PDT2map In arbitrary units (arbitrary). Combined PD/T2 maps
are REQUIRED to use this suffix regardless of the
method used to generate them.
Proton density image PDmap In arbitrary units (arbitrary). PD maps are
REQUIRED to use this suffix regardless of the
method used to generate them.
Longitudinal relaxation rate image R1map In seconds-1 (1/s). R1 maps (R1 = 1/T1) are
REQUIRED to use this suffix regardless of the
method used to generate them.
True transverse relaxation rate image R2map In seconds-1 (1/s). R2 maps (R2 = 1/T2) are
REQUIRED to use this suffix regardless of the
method used to generate them.


Name suffix Description

Observed transverse relaxation rate image R2starmap In seconds-1 (1/s). R2-star maps (R2star = 1/T2star)
are REQUIRED to use this suffix regardless of the
method used to generate them.
RF receive sensitivity map RB1map In arbitrary units (arbitrary). Radio frequency (RF)
receive (B1-) sensitivity maps are REQUIRED to use
this suffix regardless of the method used to generate
them. RB1map intensity values are
RECOMMENDED to be represented as percent
multiplicative factors such that Amplitudeeffective =
B1-intensity*Amplitudeideal.
Observed signal amplitude (S0) image S0map In arbitrary units (arbitrary). For a multi-echo
(typically fMRI) sequence, S0 maps index the baseline
signal before exponential (T2-star) signal decay. In
other words: the exponential of the intercept for a
linear decay model across log-transformed echos. For
more information, please see, for example,the tedana
documentation. S0 maps are RECOMMENDED to use
this suffix if derived from an ME-FMRI dataset.
Longitudinal relaxation time image T1map In seconds (s). T1 maps are REQUIRED to use this
suffix regardless of the method used to generate them.
Seethis interactive book on T1 mappingfor further
reading on T1-mapping.
T1 in rotating frame (T1 rho) image T1rho In seconds (s). T1-rho maps are REQUIRED to use
this suffix regardless of the method used to generate
them.
True transverse relaxation time image T2map In seconds (s). T2 maps are REQUIRED to use this
suffixregardlessofthemethodusedtogeneratethem.
Observed transverse relaxation time image T2starmap In seconds (s). T2-star maps are REQUIRED to use
this suffix regardless of the method used to generate
them.
RF transmit field image TB1map In arbitrary units (arbitrary). Radio frequency (RF)
transmit (B1+) field maps are REQUIRED to use this
suffix regardless of the method used to generate them.
TB1map intensity values are RECOMMENDED to be
represented as percent multiplicative factors such
that FlipAngleeffective =
B1+intensity*FlipAnglenominal.


Parametricimageslistedinthetableabovearetypicallygeneratedbyprocessingafilecollection. Pleasevisitthefilecollectionsappendixtoseethelistofsuffixesavailable
for quantitative MRI (qMRI) applications associated with these maps. For any other details on the organization of parametric maps, their recommended metadata fields,
and the application specific entity or metadata requirement levels of file collections that can generate them, visit the qMRI appendix.

#### Deprecated suffixes.

Some suffixes that were available in versions of the specification prior to 1.5.0 have been deprecated. These suffixes are ambiguous and have been superseded by more
precise conventions. Therefore, they are not recommended for use in new datasets. They are, however, still valid suffixes, to maintain backwards compatibility.

The following suffixes are valid, but SHOULD NOT be used for new BIDS compatible datasets (created after version 1.5.0.):

```
Name suffix Description
Fast-Low-Angle-Shot image FLASH FLASH (Fast-Low-Angle-Shot) is a vendor-specific
implementation for spoiled gradient echo acquisition.
It is commonly used for rapid anatomical imaging
and also for many different qMRI applications. When
used for a single file, it does not convey any
information about the image contrast. When used in
a file collection, it may result in conflicts across
filenames of different applications. Change: Removed
from suffixes.
Proton density image PD Ambiguous, may refer to a parametric image or to a
conventional image. Change: Replaced byPDwor
PDmap.
T2* image T2star Ambiguous, may refer to a parametric image or to a
conventional image. Change: Replaced byT2starwor
T2starmap.
```
### Task (including resting state) imaging data

Currently supported image contrasts include:

```
Name suffix Description
Blood-Oxygen-Level Dependent image bold Blood-Oxygen-Level Dependent contrast (specialized
T2* weighting)
Cerebral blood volume image cbv Cerebral Blood Volume contrast (specialized T2*
weighting or difference between T1 weighted images)
```

```
Name suffix Description
Phase image phase phase. Phase information associated with magnitude
information stored in BOLD contrast. This suffix
should be replaced by the phase in conjunction with
theboldsuffix.
```
Template:

sub-<label>/
[ses-<label>/]
func/
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_ce-<label>][_rec-<label>][_dir-<label>][_run-<index>][_echo-<index>][_part-<mag|phase|real|imag>]_bold.json
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_ce-<label>][_rec-<label>][_dir-<label>][_run-<index>][_echo-<index>][_part-<mag|phase|real|imag>]_bold.nii[.gz]
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_ce-<label>][_rec-<label>][_dir-<label>][_run-<index>][_echo-<index>][_part-<mag|phase|real|imag>]_cbv.json
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_ce-<label>][_rec-<label>][_dir-<label>][_run-<index>][_echo-<index>][_part-<mag|phase|real|imag>]_cbv.nii[.gz]
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_ce-<label>][_rec-<label>][_dir-<label>][_run-<index>][_echo-<index>][_part-<mag|phase|real|imag>]_sbref.json
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_ce-<label>][_rec-<label>][_dir-<label>][_run-<index>][_echo-<index>][_part-<mag|phase|real|imag>]_sbref.nii[.gz]
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_ce-<label>][_rec-<label>][_dir-<label>][_run-<index>][_echo-<index>]_phase.json
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_ce-<label>][_rec-<label>][_dir-<label>][_run-<index>][_echo-<index>]_phase.nii[.gz]
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_ce-<label>][_rec-<label>][_dir-<label>][_run-<index>]_events.json
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_ce-<label>][_rec-<label>][_dir-<label>][_run-<index>]_events.tsv
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_ce-<label>][_rec-<label>][_dir-<label>][_run-<index>][_recording-<label>]_physio.json
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_ce-<label>][_rec-<label>][_dir-<label>][_run-<index>][_recording-<label>]_physio.tsv.gz
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_ce-<label>][_rec-<label>][_dir-<label>][_run-<index>][_recording-<label>]_stim.json
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_ce-<label>][_rec-<label>][_dir-<label>][_run-<index>][_recording-<label>]_stim.tsv.gz

Legend:

- Filename entities or directories between square brackets (for example,[_ses-<label>]) are OPTIONAL.
- Some entities may only allow specific values, in which case those values are listed in<>, separated by|.
- _<suffix>means that there are several (>6) valid suffixes for this filename pattern.
- .<extension>means that there are several (>6) valid extensions for this file type.
- [.gz]means that both the unzipped and gzipped versions of the extension are valid.

Functionalimagingconsistsoftechniquesthatsupportrapidtemporalrepetition. Thisincludes,butisnotlimitedto,taskbasedfMRI,aswellasrestingstatefMRI,which
istreatedlikeanyothertask. FortaskbasedfMRI,acorrespondingtaskeventsfile(seebelow)MUSTbeprovided(pleasenotethatthisfileisnotnecessaryforrestingstate
scans). For multiband acquisitions, one MAY also save the single-band reference image with thesbrefsuffix (for example,sub-control01_task-nback_sbref.nii.gz).

Multi-echo data MUST be split into one file per echo using theecho-<index>entity. For example:

```
sub-01/
func/
```

```
sub-01_task-cuedSGT_run-1_echo-1_bold.nii.gz
sub-01_task-cuedSGT_run-1_echo-1_bold.json
sub-01_task-cuedSGT_run-1_echo-2_bold.nii.gz
sub-01_task-cuedSGT_run-1_echo-2_bold.json
sub-01_task-cuedSGT_run-1_echo-3_bold.nii.gz
sub-01_task-cuedSGT_run-1_echo-3_bold.json
```
Please note that the<index>denotes the number/index (in the form of a nonnegative integer) of the echo not the echo time value which needs to be stored in the field
EchoTime of the separate JSON file.

Complex-valued data MUST be split into one file for each data type. For BOLD data, there are separate suffixes for magnitude (_bold) and phase (_phase) data, but
the_phasesuffix is deprecated. Newly generated datasets SHOULD NOT use the_phasesuffix, and the suffix will be removed from the specification in the next major
release. For backwards compatibility,_phaseis considered equivalent to_part-phase_bold. When the_phasesuffix is not used, each file shares the same name with the
exception of thepart-<mag|phase>orpart-<real|imag>entity.

For example:

```
sub-01/
func/
sub-01_task-cuedSGT_part-mag_bold.nii.gz
sub-01_task-cuedSGT_part-mag_bold.json
sub-01_task-cuedSGT_part-phase_bold.nii.gz
sub-01_task-cuedSGT_part-phase_bold.json
sub-01_task-cuedSGT_part-mag_sbref.nii.gz
sub-01_task-cuedSGT_part-mag_sbref.json
sub-01_task-cuedSGT_part-phase_sbref.nii.gz
sub-01_task-cuedSGT_part-phase_sbref.json
```
Some meta information about the acquisition MUST be provided in an additional JSON file.

#### Required fields


Key name Requirement Level Data type Description

RepetitionTime REQUIRED mutually exclusive with
VolumeTiming

number The time in seconds between the
beginning of an acquisition of one
volume and the beginning of
acquisition of the volume following it
(TR). When used in the context of
functional acquisitions this parameter
best corresponds toDICOM Tag 0020,
0110 : the ”time delta between images in
a dynamic of functional set of images”
but may also be found inDICOM Tag
0018, 0080: ”the period of time in msec
between the beginning of a pulse
sequence and the beginning of the
succeeding (essentially identical) pulse
sequence”. This definition includes time
between scans (when no data has been
acquired) in case of sparse acquisition
schemes. This value MUST be
consistent with the ’pixdim[4]’ field
(after accounting for units stored in
’xyzt_units’ field) in the NIfTI header.
This field is mutually exclusive with
VolumeTiming. Must be a number
greater than 0.
VolumeTiming REQUIRED mutually exclusive with
RepetitionTime

```
arrayofnumbers The time at which each volume was
acquired during the acquisition. It is
described using a list of times referring
to the onset of each volume in the
BOLD series. The list must have the
same length as the BOLD series, and the
values must be non-negative and
monotonically increasing. This field is
mutually exclusive with
"RepetitionTime"and"DelayTime".
If defined, this requires acquisition time
(TA) be defined via either
"SliceTiming"or
"AcquisitionDuration"be defined.
```

Key name Requirement Level Data type Description

TaskName REQUIRED string Name of the task. No two tasks should
have the same name. The task label
included in the file name is derived from
this"TaskName"field by removing all
non-alphanumeric characters (that is,
all except those matching
[0-9a-zA-Z]). For example
"TaskName" "faces n-back"will
correspond to task labelfacesnback. A
RECOMMENDED convention is to
name resting state task using labels
beginning withrest.

Forthefieldsdescribedaboveandinthefollowingsection, theterm”Volume”referstoareconstructionoftheobjectbeingimaged(forexample, brainorpartofabrain).
In case of multiple channels in a coil, the term ”Volume” refers to a combined image rather than an image from each coil.

#### Other RECOMMENDED metadata

Timing Parameters


Key name Requirement Level Data type Description

NumberOfVolumesDiscardedByScanner RECOMMENDED integer Number of volumes (”dummy scans”)
discarded by the scanner (as opposed to
those discarded by the user post hoc)
before saving the imaging file. For
example, a sequence that automatically
discards the first 4 volumes before
saving would have this field as 4. A
sequence that does not discard dummy
scans would have this set to 0. Please
note that the onsets recorded in the
events.tsvfile should always refer to
the beginning of the acquisition of the
first volume in the corresponding
imagingfile-independentofthevalueof
"NumberOfVolumesDiscardedByScanner"
field. Must be a number greater than or
equal to 0.
NumberOfVolumesDiscardedByUser RECOMMENDED integer Number of volumes (”dummy scans”)
discarded by the user before including
the file in the dataset. If possible,
including all of the volumes is strongly
RECOMMENDED. Please note that the
onsets recorded in theevents.tsvfile
should always refer to the beginning of
the acquisition of the first volume in the
corresponding imaging file -
independent of the value of
"NumberOfVolumesDiscardedByUser"
field. Must be a number greater than or
equal to 0.


Key name Requirement Level Data type Description

DelayTime RECOMMENDED number User specified time (in seconds) to delay
the acquisition of data for the following
volume. If the field is not present it is
assumed to be set to zero. Corresponds
to Siemens CSA header field
lDelayTimeInTR. This field is
REQUIRED for sparse sequences using
the"RepetitionTime"field that do not
have the"SliceTiming"field set to
allowed for accurate calculation of
”acquisition time”. This field is
mutually exclusive with
"VolumeTiming".
AcquisitionDuration RECOMMENDED, but REQUIRED for
sequences that are described with the
VolumeTimingfield and that do not
have theSliceTimingfield set to allow
for accurate calculation of ”acquisition
time”

number Duration (in seconds) of volume
acquisition. Corresponds to DICOM Tag
0018, 9073Acquisition Duration.
This field is mutually exclusive with
"RepetitionTime". Must be a number
greater than 0.
DelayAfterTrigger RECOMMENDED number Duration (in seconds) from trigger
delivery to scan onset. This delay is
commonly caused by adjustments and
loading times. This specification is
entirely independent of
"NumberOfVolumesDiscardedByScanner"
or
"NumberOfVolumesDiscardedByUser",
as the delay precedes the acquisition.

The following table recapitulates the different ways that specific fields have to be populated for functional sequences. Note that all these options can be used for non
sparse sequences but that only options B, D and E are valid for sparse sequences.

```
RepetitionTime SliceTiming AcquisitionDuration DelayTime VolumeTiming
option A [ X ] [ ] [ ]
option B [ ] [ X ] [ ] [ X ]
option C [ ] [ X ] [ ] [ X ]
option D [ X ] [ X ] [ ] [ ]
```

```
RepetitionTime SliceTiming AcquisitionDuration DelayTime VolumeTiming
option E [ X ] [ ] [ X ] [ ]
```
Legend

- [ X ] --> MUST be defined
□--> MUST NOT be defined
- empty cell --> MAY be specified

fMRI task information

Key name Requirement Level Data type Description

Instructions RECOMMENDED string Text of the instructions given to
participants before the recording. This
is especially important in context of
resting state recordings and
distinguishing between eyes open and
eyes closed paradigms.
TaskDescription RECOMMENDED string Longer description of the task.
CogAtlasID RECOMMENDED string CogAtlasID of the corresponding
Cognitive AtlasTask term.
CogPOID RECOMMENDED string CogPOID of the correspondingCogPO
term.

See Common metadata fields for a list of additional terms and their definitions.

Example:

```
sub-01/
func/
sub-control01_task-nback_bold.json
```
{
"TaskName":"N Back",
"RepetitionTime": 0.8,
"EchoTime":0.03,
"FlipAngle": 78 ,
"SliceTiming":[0.0, 0.2, 0.4, 0.6,0.0,0.2,0.4,0.6, 0.0, 0.2, 0.4,0.6,0.0,0.2, 0.4, 0.6],
"MultibandAccelerationFactor": 4 ,


"ParallelReductionFactorInPlane": 2 ,
"PhaseEncodingDirection": "j",
"InstitutionName":"Stanford University",
"InstitutionAddress": "450 Serra Mall, Stanford, CA 94305-2004, USA",
"DeviceSerialNumber": "11035",
"B0FieldSource": ["phasediff_fmap0","pepolar_fmap0"]
}

### Diffusion imaging data.

Severalexample datasetscontain diffusion imaging data formatted using this specification and that can be used for practical guidance when curating a new dataset:

- genetics_ukbb
- eeg_rest_fmri
- ds114
- ds000117

Diffusion-weighted imaging data acquired for a participant. Currently supported image types include:

```
Name suffix Description
Diffusion-weighted image dwi Diffusion-weighted imaging contrast (specialized T2
weighting).
Single-band reference image sbref Single-band reference for one or more multi-banddwi
images.
```
Template:

sub-<label>/
[ses-<label>/]
dwi/
sub-<label>[_ses-<label>][_acq-<label>][_rec-<label>][_dir-<label>][_run-<index>][_part-<mag|phase|real|imag>]_dwi.bval
sub-<label>[_ses-<label>][_acq-<label>][_rec-<label>][_dir-<label>][_run-<index>][_part-<mag|phase|real|imag>]_dwi.bvec
sub-<label>[_ses-<label>][_acq-<label>][_rec-<label>][_dir-<label>][_run-<index>][_part-<mag|phase|real|imag>]_dwi.json
sub-<label>[_ses-<label>][_acq-<label>][_rec-<label>][_dir-<label>][_run-<index>][_part-<mag|phase|real|imag>]_dwi.nii[.gz]
sub-<label>[_ses-<label>][_acq-<label>][_rec-<label>][_dir-<label>][_run-<index>][_part-<mag|phase|real|imag>]_sbref.json
sub-<label>[_ses-<label>][_acq-<label>][_rec-<label>][_dir-<label>][_run-<index>][_part-<mag|phase|real|imag>]_sbref.nii[.gz]
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_rec-<label>][_dir-<label>][_run-<index>][_recording-<label>]_physio.json
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_rec-<label>][_dir-<label>][_run-<index>][_recording-<label>]_physio.tsv.gz
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_rec-<label>][_dir-<label>][_run-<index>][_recording-<label>]_stim.json
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_rec-<label>][_dir-<label>][_run-<index>][_recording-<label>]_stim.tsv.gz


Legend:

- Filename entities or directories between square brackets (for example,[_ses-<label>]) are OPTIONAL.
- Some entities may only allow specific values, in which case those values are listed in<>, separated by|.
- _<suffix>means that there are several (>6) valid suffixes for this filename pattern.
- .<extension>means that there are several (>6) valid extensions for this file type.
- [.gz]means that both the unzipped and gzipped versions of the extension are valid.

Therun-<index>entity is RECOMMENDED to encode the splits of multipart DWI scans (see below for more information on multipart DWI schemes).

Combining multi- and single-band acquisitions. The single-band reference image MAY be stored with suffixsbref(for example,dwi/sub-control01_sbref.nii[.gz])
as long as the image has no correspondinggradient information ([*_]dwi.bvaland[*_]dwi.bvecsidecar files)to be stored.

Otherwise, if some gradient information is associated to the single-band diffusion image and a multi-band diffusion image also exists, theacq-<label>entity MUST be
usedtodistinguishbothimages. Insuchacase,twofilescouldhavethefollowingnames:sub-01_acq-singleband_dwi.nii.gzandsub-01_acq-multiband_dwi.nii.gz.
The user is free to choose any other label thansinglebandandmultiband, as long as they are consistent across subjects and sessions.

#### REQUIRED gradient orientation information.

The REQUIRED gradient orientation information corresponding to a DWI acquisition MUST be stored using[*_]dwi.bvaland[*_]dwi.bvecpairs of files. The
[*_]dwi.bvaland[*_]dwi.bvecfiles MAY be saved on any level of the directory structure and thus define those values for all sessions and/or subjects in one place
(see the inheritance principle).

As an exception to the common principles that parameters are constant across runs, the gradient table information (stored within the[*_]dwi.bvaland[*_]dwi.bvec
files) MAY change across DWI runs.

Gradientorientationfileformats. The[*_]dwi.bvaland[*_]dwi.bvecfilesMUSTfollowtheFSLformat: The[*_]dwi.bvecfilecontains3rowswithNspace-delimited
floating-point numbers (corresponding to the N volumes in the corresponding NIfTI file.) The first row contains the x elements, the second row contains the y elements
andthethirdrowcontainsthezelementsofaunitvectorinthedirectionoftheapplieddiffusiongradient, wherethei-thelementsineachrowcorrespondtogethertothe
i-th volume, with[0,0,0]for non-diffusion-weighted (also called b=0 or low-b) volumes. Following the FSL format for the[*_]dwi.bvecspecification, the coordinate
system of the b vectors MUST be defined with respect to the coordinate system defined by the header of the corresponding_dwiNIfTI file and not the scanner’s device
coordinate system (see Coordinate systems). The most relevant limitation imposed by this choice is that the gradient information cannot be directly stored in this format
if the scanner generates b-vectors in scanner coordinates.

Example of[*_]dwi.bvecfile, with N=6, with two b=0 volumes in the beginning:

0 0 0.021828 -0.015425 -0.70918 -0.2465
0 0 0.80242 0.22098 -0.00063106 0.1043
0 0 -0.59636 0.97516 -0.70503 -0.96351

The[*_]dwi.bvalfile contains the b-values (in s/mm2) corresponding to the volumes in the relevant NIfTI file), with 0 designating b=0 volumes, space-delimited.

Example of[*_]dwi.bvalfile, corresponding to the previous[*_]dwi.bvecexample:

0 0 2000 2000 1000 1000


#### Multipart (split) DWI schemes

Some MR schemes cannot be acquired directly by some scanner devices, requiring to generate several DWI runs that were originally meant to belong in a single one. For
instance, some GE scanners cannot collect more than ≈160 volumes in a single run under fast-changing gradients, so acquiring HCP-style diffusion images will require
splittingtheDWIschemeinseveralruns. Becauseresearcherswillgenerallyoptimizethedatasplits,thesewilllikelynotbeabletobedirectlyconcatenated. BIDSpermits
defining arbitrary groupings of these multipart scans with the following metadata:

Key name Requirement Level Data type Description

MultipartID REQUIRED string A unique (per participant) label tagging
DWI runs that are part of a multipart
scan.

JSON example:

{
"MultipartID": "dwi_1"
}

Forinstance,iftherearetwophase-encodingdirections(AP,PA),andtworunseach,andtheintentoftheresearcheristhatallofthemarepartofauniquemultipartscan,
then they will tag all four runs with the sameMultipartID(shown at the right-hand side of the file listing):

```
sub-1/
dwi # MultipartID/
sub-1_dir-AP_run-1_dwi.nii.gz # dwi_1
sub-1_dir-AP_run-2_dwi.nii.gz # dwi_1
sub-1_dir-PA_run-1_dwi.nii.gz # dwi_1
sub-1_dir-PA_run-2_dwi.nii.gz # dwi_1
```
If, conversely, the researcher wanted to store two multipart scans, one possibility is to combine matching phase-encoding directions:

```
sub-1/
dwi # MultipartID/
sub-1_dir-AP_run-1_dwi.nii.gz # dwi_1
sub-1_dir-AP_run-2_dwi.nii.gz # dwi_1
sub-1_dir-PA_run-1_dwi.nii.gz # dwi_2
sub-1_dir-PA_run-2_dwi.nii.gz # dwi_2
```
Alternatively, the researcher’s intent could be combining opposed phase-encoding runs instead:

```
sub-1/
dwi # MultipartID/
sub-1_dir-AP_run-1_dwi.nii.gz # dwi_1
sub-1_dir-AP_run-2_dwi.nii.gz # dwi_2
```

```
sub-1_dir-PA_run-1_dwi.nii.gz # dwi_1
sub-1_dir-PA_run-2_dwi.nii.gz # dwi_2
```
TheMultipartIDmetadata MAY be used with theacq-<label>entity, for example:

```
sub-1/
dwi # MultipartID/
sub-1_acq-shell1_run-1_dwi.nii.gz # dwi_1
sub-1_acq-shell1_run-2_dwi.nii.gz # dwi_2
sub-1_acq-shell2_run-1_dwi.nii.gz # dwi_1
sub-1_acq-shell2_run-2_dwi.nii.gz # dwi_2
```
#### Other RECOMMENDED metadata

ThePhaseEncodingDirectionandTotalReadoutTimemetadatafieldsareRECOMMENDEDtoenablethecorrectionofgeometricaldistortionswithfieldmapinformation.
See Common metadata fields for a list of additional terms that can be included in the corresponding JSON file.

JSON example:

{
"PhaseEncodingDirection":"j-",
"TotalReadoutTime":0.095,
"B0FieldSource":["phasediff_fmap0","pepolar_fmap0"]
}

### Arterial Spin Labeling perfusion data

Severalexample ASL datasetshave been formatted using this specification and can be used for practical guidance when curating a new dataset.

Template:

sub-<label>/
[ses-<label>/]
perf/
sub-<label>[_ses-<label>][_acq-<label>][_rec-<label>][_dir-<label>][_run-<index>]_asl.json
sub-<label>[_ses-<label>][_acq-<label>][_rec-<label>][_dir-<label>][_run-<index>]_asl.nii[.gz]
sub-<label>[_ses-<label>][_acq-<label>][_rec-<label>][_dir-<label>][_run-<index>]_m0scan.json
sub-<label>[_ses-<label>][_acq-<label>][_rec-<label>][_dir-<label>][_run-<index>]_m0scan.nii[.gz]
sub-<label>[_ses-<label>][_acq-<label>][_rec-<label>][_dir-<label>][_run-<index>]_aslcontext.json
sub-<label>[_ses-<label>][_acq-<label>][_rec-<label>][_dir-<label>][_run-<index>]_aslcontext.tsv
sub-<label>[_ses-<label>][_acq-<label>][_rec-<label>][_run-<index>]_asllabeling.jpg
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_rec-<label>][_dir-<label>][_run-<index>][_recording-<label>]_physio.json
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_rec-<label>][_dir-<label>][_run-<index>][_recording-<label>]_physio.tsv.gz


```
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_rec-<label>][_dir-<label>][_run-<index>][_recording-<label>]_stim.json
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_rec-<label>][_dir-<label>][_run-<index>][_recording-<label>]_stim.tsv.gz
```
Legend:

- Filename entities or directories between square brackets (for example,[_ses-<label>]) are OPTIONAL.
- Some entities may only allow specific values, in which case those values are listed in<>, separated by|.
- _<suffix>means that there are several (>6) valid suffixes for this filename pattern.
- .<extension>means that there are several (>6) valid extensions for this file type.
- [.gz]means that both the unzipped and gzipped versions of the extension are valid.

ThecompleteASLtimeseriesshouldbestoredasa4DNIfTIfileintheoriginalacquisitionorder, accompaniedbytwoancillaryfiles:*_asl.jsonand*_aslcontext.tsv.

#### *_aslcontext.tsv.

The*_aslcontext.tsvtable consists of a single column of labels identifying thevolume_typeof each volume in the corresponding*_asl.nii[.gz]file. Volume types
are defined in the following table, based on DICOM Tag 0018, 9257ASL Context. Note that the volume_typescontrolandlabelwithin BIDS only serve to specify the
magnetization state of the blood and thus the ASL subtraction order. See the ASL Appendix for more information oncontrolandlabel.

volume_type Definition

control The control image is acquired in the exact same way as the label image, except
that the magnetization of the blood flowing into the imaging region has not been
inverted.
label The label image is acquired in the exact same way as the control image, except
that the blood magnetization flowing into the imaging region has been inverted.
m0scan The M0 image is a calibration image, used to estimate the equilibrium
magnetization of blood.
deltam The deltaM image is a perfusion-weighted image, obtained by the subtraction of
control-label.
cbf The cerebral blood flow (CBF) image is produced by dividing the deltaM by the M0,
quantified intomL/100g/min(See alsodoi:10.1002/mrm.25197).

If thecontrolandlabelimages are not available, their derivativedeltamshould be stored within the*_asl.nii[.gz]and specified in the*_aslcontext.tsvinstead.
If thedeltamis not available,cbfshould be stored within the*_asl.nii[.gz]and specified in the*_aslcontext.tsv. Whencbfis stored within the*_asl.nii[.gz],
its units need to be specified in the*_asl.jsonas well. Note that the raw images, including them0scan, may also be used for quality control. See the ASL Appendix for
examples of the three possible cases, in order of decreasing preference.

#### Scaling.

The*_asl.nii.gzand*_m0scan.nii.gzshouldcontainappropriatelyscaleddata,andnoadditionalscalingfactorsareallowedotherthanthescaleslopeintherespective
NIfTI headers.


#### M0.

Them0scancan either be stored inside the 4D ASL time-series NIfTI file or as a separate NIfTI file, depending on whether it was acquired within the ASL
time-series or as a separate scan. These and other M0 options are specified in the REQUIREDM0Typefield of the*_asl.jsonfile. It can also be stored under
fmap/sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>]_dir-<label>[_run-<index>]_m0scan.nii[.gz], when the pepolar approach is used.

#### *_asl.jsonfile.

DependingonthemethodusedforASLacquisition((P)CASLorPASL)differentmetadatafieldsareapplicable. Additionally,somecommonmetadatafieldsareREQUIRED
for the*_asl.json:MagneticFieldStrength,MRAcquisitionType,EchoTime,SliceTimingin caseMRAcquisitionTypeis defined as 2D,RepetitionTimePreparation,
andFlipAnglein caseLookLockeristrue. See the ASL Appendix for more information on the most common ASL sequences.

Common metadata fields applicable to both (P)CASL and PASL

Key name Requirement Level Data type Description

ArterialSpinLabelingType REQUIRED string The arterial spin labeling type. Must be
one of:"CASL","PCASL","PASL".
PostLabelingDelay REQUIRED numberorarrayofnumbers This is the postlabeling delay (PLD)
time, in seconds, after the end of the
labeling (for"CASL"or"PCASL") or
middle of the labeling pulse (for
"PASL") until the middle of the
excitation pulse applied to the imaging
slab (for 3D acquisition) or first slice
(for 2D acquisition). Can be a number
(for a single-PLD time series) or an
array of numbers (for multi-PLD and
Look-Locker). In the latter case, the
array of numbers contains the PLD of
each volume, namely eachcontroland
label, in the acquisition order. Any
image within the time-series without a
PLD, for example anm0scan, is
indicated by a zero. Based on DICOM
Tags 0018, 9079Inversion Timesand
0018, 0082InversionTime.
BackgroundSuppression REQUIRED boolean Boolean indicating if background
suppression is used. Must be one of:
"true","false".


Key name Requirement Level Data type Description

M0Type REQUIRED string Describes the presence of M0
information."Separate"means that a
separate*_m0scan.nii[.gz]is present.
"Included"means that an m0scan
volume is contained within the current
*_asl.nii[.gz]."Estimate"means
that a single whole-brain M0 value is
provided."Absent"means that no
specific M0 information is present. Must
be one of:"Separate","Included",
"Estimate","Absent".
TotalAcquiredPairs REQUIRED number The total number of acquired
control-labelpairs. A single pair
consists of a singlecontroland a single
labelimage. Must be a number greater
than 0.
VascularCrushing RECOMMENDED boolean Boolean indicating if Vascular Crushing
is used. Corresponds to DICOM Tag
0018, 9259ASL Crusher Flag. Must be
one of:"true","false".
AcquisitionVoxelSize RECOMMENDED arrayofnumbers An array of numbers with a length of 3,
in millimeters. This parameter denotes
the original acquisition voxel size,
excluding any inter-slice gaps and
before any interpolation or resampling
within reconstruction or image
processing. Any point spread function
effects, for example due to T2-blurring,
that would decrease the effective
resolution are not considered here.
LabelingOrientation RECOMMENDED arrayofnumbers Orientation of the labeling plane
((P)CASL) or slab (PASL). The direction
cosines of a normal vector
perpendicular to the ASL labeling slab
or plane with respect to the patient.
Corresponds to DICOM Tag 0018, 9255
ASL Slab Orientation.


Key name Requirement Level Data type Description

LabelingDistance RECOMMENDED number Distance from the center of the imaging
slab to the center of the labeling plane
((P)CASL) or the leading edge of the
labeling slab (PASL), in millimeters. If
the labeling is performed inferior to the
isocenter, this number should be
negative. Based on DICOM macro
C.8.13.5.14.
LabelingLocationDescription RECOMMENDED string Description of the location of the
labeling plane ("CASL"or"PCASL") or
the labeling slab ("PASL") that cannot
be captured by fields
LabelingOrientationor
LabelingDistance. May include a link
to an anonymized screenshot of the
planning of the labeling slab/plane with
respect to the imaging slab or slices
*_asllabeling.jpg. Based on DICOM
macro C.8.13.5.14.
LookLocker OPTIONAL boolean Boolean indicating if a Look-Locker
readout is used. Must be one of:"true",
"false".
LabelingEfficiency OPTIONAL number Labeling efficiency, specified as a
number between zero and one, only if
obtained externally (for example
phase-contrast based). Must be a
number greater than 0.
M0Estimate OPTIONAL, but REQUIRED ifM0Type
isEstimate

number A single numerical whole-brain M0
value (referring to the M0 of blood),
only if obtained externally (for example
retrieved from CSF in a separate
measurement). Must be a number
greater than 0.
BackgroundSuppressionNumberPulses OPTIONAL, but RECOMMENDED if
BackgroundSuppressionistrue

```
number The number of background suppression
pulses used. Note that this excludes any
effect of background suppression pulses
applied before the labeling. Must be a
number greater than or equal to 0.
```

Key name Requirement Level Data type Description

BackgroundSuppressionPulseTime OPTIONAL, but RECOMMENDED if
BackgroundSuppressionistrue

arrayofnumbers Array of numbers containing timing, in
seconds, of the background suppression
pulses with respect to the start of the
labeling. In case of multi-PLD with
different background suppression pulse
times, only the pulse time of the first
PLD should be defined.
VascularCrushingVENC OPTIONAL, but RECOMMENDED if
VascularCrushingistrue

```
numberorarrayofnumbers The crusher gradient strength, in
centimeters per second. Specify either
one number for the total time-series, or
provide an array of numbers, for
example when using QUASAR, using
the value zero to identify volumes for
whichVascularCrushingwas turned
off. Corresponds to DICOM Tag 0018,
925AASL Crusher Flow Limit.
```
(P)CASL-specific metadata fields

These fields can only be used whenArterialSpinLabelingTypeis"CASL"or"PCASL". See the ASL Appendix for more information on the (P)CASL sequence and the
Labeling Pulse fields.

Key name Requirement Level Data type Description

PCASLType RECOMMENDED if
ArterialSpinLabelingTypeis"PCASL"

string The type of gradient pulses used in the
controlcondition. Must be one of:
"balanced","unbalanced".
CASLType RECOMMENDED if
ArterialSpinLabelingTypeis"CASL"

```
string Describes if a separate coil is used for
labeling. Must be one of:
"single-coil","double-coil".
```

Key name Requirement Level Data type Description

LabelingDuration REQUIRED numberorarrayofnumbers Total duration of the labeling pulse
train, in seconds, corresponding to the
temporal width of the labeling bolus for
"PCASL"or"CASL". In case all
control-label volumes (or deltam or
CBF) have the sameLabelingDuration,
a scalar must be specified. In case the
control-label volumes (or deltam or cbf)
have a different"LabelingDuration",
an array of numbers must be specified,
for which anym0scanin the timeseries
has a"LabelingDuration"of zero. In
caseanarrayofnumbersisprovided,its
length should be equal to the number of
volumes specified in*_aslcontext.tsv.
Corresponds to DICOM Tag 0018, 9258
ASL Pulse Train Duration.
LabelingPulseAverageGradient RECOMMENDED number The average labeling gradient, in
milliteslas per meter. Must be a number
greater than 0.
LabelingPulseMaximumGradient RECOMMENDED number The maximum amplitude of the
gradient switched on during the
application of the labeling RF pulse(s),
in milliteslas per meter. Must be a
number greater than 0.
LabelingPulseAverageB1 RECOMMENDED number The average B1-field strength of the RF
labeling pulses, in microteslas. As an
alternative,
"LabelingPulseFlipAngle"can be
provided. Must be a number greater
than 0.
LabelingPulseDuration RECOMMENDED number Duration of the individual labeling
pulses, in milliseconds. Must be a
number greater than 0.


Key name Requirement Level Data type Description

LabelingPulseFlipAngle RECOMMENDED number The flip angle of a single labeling pulse,
in degrees, which can be given as an
alternative to
"LabelingPulseAverageB1". Must be a
number greater than 0 and less than or
equal to 360.
LabelingPulseInterval RECOMMENDED number Delay between the peaks of the
individual labeling pulses, in
milliseconds. Must be a number greater
than 0.

PASL-specific metadata fields

These fields can only be used whenArterialSpinLabelingTypeisPASL. See the ASL Appendix for more information on the PASL sequence and the BolusCutOff fields.

Key name Requirement Level Data type Description

BolusCutOffFlag REQUIRED boolean Boolean indicating if a bolus cut-off
technique is used. Corresponds to
DICOM Tag 0018, 925CASL Bolus
Cut-off Flag. Must be one of:"true",
"false".
PASLType RECOMMENDED string Type of the labeling pulse of thePASL
labeling, for example"FAIR",
"EPISTAR", or"PICORE".
LabelingSlabThickness RECOMMENDED number Thickness of the labeling slab in
millimeters. For non-selective FAIR a
zero is entered. Corresponds to DICOM
Tag 0018, 9254ASL Slab Thickness.
Must be a number greater than 0.


Key name Requirement Level Data type Description

BolusCutOffDelayTime OPTIONAL, but REQUIRED if
BolusCutOffFlagistrue

numberorarrayofnumbers Duration between the end of the
labeling and the start of the bolus
cut-off saturation pulse(s), in seconds.
This can be a number or array of
numbers, of which the values must be
non-negative and monotonically
increasing, depending on the number of
bolus cut-off saturation pulses. For
Q2TIPS,onlythevaluesforthefirstand
last bolus cut-off saturation pulses are
provided. Based on DICOM Tag 0018,
925FASL Bolus Cut-off Delay Time.
BolusCutOffTechnique OPTIONAL, but REQUIRED if
BolusCutOffFlagistrue

```
string Name of the technique used, for
example"Q2TIPS","QUIPSS",
"QUIPSSII". Corresponds to DICOM
Tag 0018, 925EASL Bolus Cut-off
Technique.
```
#### m0scanmetadata fields

Some common metadata fields are REQUIRED for the*_m0scan.json:EchoTime,RepetitionTimePreparation, andFlipAnglein caseLookLockeristrue.

Key name Requirement Level Data type Description

IntendedFor REQUIRED stringorarray The paths to files for which the
associated file is intended to be used.
Contains one or more IntendedFor.
Using forward-slash separated paths
relative to the participant subdirectory
is IntendedFor. This is used to refer to
the ASL time series for which the
*_m0scan.nii[.gz]is intended.


Key name Requirement Level Data type Description

AcquisitionVoxelSize RECOMMENDED arrayofnumbers An array of numbers with a length of 3,
in millimeters. This parameter denotes
the original acquisition voxel size,
excluding any inter-slice gaps and
before any interpolation or resampling
within reconstruction or image
processing. Any point spread function
effects, for example due to T2-blurring,
that would decrease the effective
resolution are not considered here.

The following table recapitulates the ASL field dependencies. If Source field (column 1) contains the Value specified in column 2, then the Requirements in column 4 are
imposed on the Dependent fields in column 3. See the ASL Appendix for this information in the form of flowcharts.

```
Source field Value Dependent field Requirements
MRAcquisitionType 2D / 3D SliceTiming [X] / []
LookLocker true FlipAngle [X]
ArterialSpinLabelingType PCASL LabelingDuration [X]
ArterialSpinLabelingType PASL BolusCutOffFlag [X]
BolusCutOffFlag true / false BolusCutOffDelayTime [X] / []
BolusCutOffFlag true / false BolusCutOffTechnique [X] / []
M0Type Separate */perf/ contains*_m0scan.nii[.gz]and*_m0scan.json
M0Type Included *_aslcontext.tsv contains m0scan
M0Type Estimate M0Estimate [X]
*_aslcontext.tsv cbf Units [X]
```
Legend

- [ X ] --> MUST be defined
□--> MUST NOT be defined

### Fieldmap data

Data acquired to correct for B0 inhomogeneities can come in different forms. The current version of this standard considers four different scenarios:

1. Phase-difference map
2. Two phase maps


3. Direct field mapping
4. ”PEpolar” fieldmaps

These four different types of field mapping strategies can be encoded using the following image types:

```
Name suffix Description
EPI epi The phase-encoding polarity (PEpolar) technique
combines two or more Spin Echo EPI scans with
different phase encoding directions to estimate the
underlying inhomogeneity/deformation map.
Fieldmap fieldmap Some MR schemes such as spiral-echo imaging (SEI)
sequences are able to directly provide maps of the B0
field inhomogeneity.
Magnitude magnitude Field-mapping MR schemes such as gradient-recalled
echo (GRE) generate a Magnitude image to be used
for anatomical reference. Requires the existence of
Phase, Phase-difference or Fieldmap maps.
Magnitude magnitude1 MagnitudemapgeneratedbyGREorsimilarschemes,
associated with the first echo in the sequence.
Magnitude magnitude2 MagnitudemapgeneratedbyGREorsimilarschemes,
associated with the second echo in the sequence.
Phase phase1 Phase map generated by GRE or similar schemes,
associated with the first echo in the sequence.
Phase phase2 Phase map generated by GRE or similar schemes,
associated with the second echo in the sequence.
Phase-difference phasediff Some scanners subtract thephase1from thephase2
map and generate a uniquephasedifffile. For
instance, this is a common output for the built-in
fieldmap sequence of Siemens scanners.
```
#### Expressing the MR protocol intent for fieldmaps

Fieldmaps are typically acquired with the purpose of correcting one or more EPI scans underdwi/,func/, orperf/for distortions derived from B0 nonuniformity.

Using **B0FieldIdentifier** metadata

The general purposeB0FieldIdentifierMRI metadata is RECOMMENDED for the prescription of the B0 field estimation intent of the original acquisition protocol.
B0FieldIdentifierandB0FieldSourceduplicate the capabilities of the originalIntendedForapproach (see below), while permitting more complex use cases. It is
RECOMMENDED to use both approaches to maintain compatibility with tools that support older datasets.


Using **IntendedFor** metadata

Fieldmap data MAY be linked to the specific scan(s) it was acquired for by filling theIntendedForfield in the corresponding JSON file.

Key name Requirement Level Data type Description

IntendedFor OPTIONAL stringorarray The paths to files for which the
associated file is intended to be used.
Contains one or more IntendedFor.
Using forward-slash separated paths
relative to the participant subdirectory
is IntendedFor. This field is OPTIONAL,
and in case the fieldmaps do not
correspond to any particular scans, it
does not have to be filled.

For example:

{
"IntendedFor":[
"bids::sub-01/ses-pre/func/sub-01_ses-pre_task-motor_run-1_bold.nii.gz",
"bids::sub-01/ses-pre/func/sub-01_ses-pre_task-motor_run-2_bold.nii.gz"
]
}

#### Types of fieldmaps.

Case 1: Phase-difference map and at least one magnitude image

Example datasetscontaining that type of fieldmap can be found here:

- 7t_trt
- genetics_ukbb
- ds000117

Template:

sub-<label>/
[ses-<label>/]
fmap/
sub-<label>[_ses-<label>][_acq-<label>][_run-<index>]_magnitude1.json
sub-<label>[_ses-<label>][_acq-<label>][_run-<index>]_magnitude1.nii[.gz]
sub-<label>[_ses-<label>][_acq-<label>][_run-<index>]_magnitude2.json


```
sub-<label>[_ses-<label>][_acq-<label>][_run-<index>]_magnitude2.nii[.gz]
sub-<label>[_ses-<label>][_acq-<label>][_run-<index>]_phasediff.json
sub-<label>[_ses-<label>][_acq-<label>][_run-<index>]_phasediff.nii[.gz]
```
Legend:

- Filename entities or directories between square brackets (for example,[_ses-<label>]) are OPTIONAL.
- Some entities may only allow specific values, in which case those values are listed in<>, separated by|.
- _<suffix>means that there are several (>6) valid suffixes for this filename pattern.
- .<extension>means that there are several (>6) valid extensions for this file type.
- [.gz]means that both the unzipped and gzipped versions of the extension are valid.

where the REQUIRED_phasediffimage corresponds to the phase-drift map between echo times, the REQUIRED_magnitude1image corresponds to the shorter echo
time, and the OPTIONAL_magnitude2image to the longer echo time.

Required fields:

Key name Requirement Level Data type Description

EchoTime1 REQUIRED number The time (in seconds) when the first
(shorter) echo occurs. Must be a number
greater than 0.
EchoTime2 REQUIRED number The time (in seconds) when the second
(longer) echo occurs. Must be a number
greater than 0.

In this particular case, the sidecar JSON filesub-<label>[_ses-<label>][_acq-<label>][_run-<index>]_phasediff.jsonMUST define the time of two echos used to
map the phase and finally calculate the phase-difference map. For example:

{
"EchoTime1": 0.00600,
"EchoTime2": 0.00746,
"B0FieldIdentifier": "phasediff_fmap0"
}

Case 2: Two phase maps and two magnitude images

Similar to case 1, but instead of a precomputed phase-difference map, two separate phase images and two magnitude images corresponding to first and second echos are
available.

Template:

sub-<label>/
[ses-<label>/]


```
fmap/
sub-<label>[_ses-<label>][_acq-<label>][_run-<index>]_magnitude1.json
sub-<label>[_ses-<label>][_acq-<label>][_run-<index>]_magnitude1.nii[.gz]
sub-<label>[_ses-<label>][_acq-<label>][_run-<index>]_magnitude2.json
sub-<label>[_ses-<label>][_acq-<label>][_run-<index>]_magnitude2.nii[.gz]
sub-<label>[_ses-<label>][_acq-<label>][_run-<index>]_phase1.json
sub-<label>[_ses-<label>][_acq-<label>][_run-<index>]_phase1.nii[.gz]
sub-<label>[_ses-<label>][_acq-<label>][_run-<index>]_phase2.json
sub-<label>[_ses-<label>][_acq-<label>][_run-<index>]_phase2.nii[.gz]
```
Legend:

- Filename entities or directories between square brackets (for example,[_ses-<label>]) are OPTIONAL.
- Some entities may only allow specific values, in which case those values are listed in<>, separated by|.
- _<suffix>means that there are several (>6) valid suffixes for this filename pattern.
- .<extension>means that there are several (>6) valid extensions for this file type.
- [.gz]means that both the unzipped and gzipped versions of the extension are valid.

Required fields:

Key name Requirement Level Data type Description

EchoTime REQUIRED number The time (in seconds) when the echo
corresponding to this map was acquired.
Must be a number greater than 0.

EachphasemaphasacorrespondingsidecarJSONfiletospecifyitscorrespondingEchoTime. Forexample,sub-<label>[_ses-<label>][_acq-<label>][_run-<index>]_phase2.json
may read:

{
"EchoTime":0.00746,
"B0FieldIdentifier": "phases_fmap0"
}

Case 3: Direct field mapping

In some cases (for example GE), the scanner software will directly reconstruct a B0 field map along with a magnitude image used for anatomical reference.

Template:

sub-<label>/
[ses-<label>/]
fmap/


```
sub-<label>[_ses-<label>][_acq-<label>][_run-<index>]_fieldmap.json
sub-<label>[_ses-<label>][_acq-<label>][_run-<index>]_fieldmap.nii[.gz]
sub-<label>[_ses-<label>][_acq-<label>][_run-<index>]_magnitude.json
sub-<label>[_ses-<label>][_acq-<label>][_run-<index>]_magnitude.nii[.gz]
```
Legend:

- Filename entities or directories between square brackets (for example,[_ses-<label>]) are OPTIONAL.
- Some entities may only allow specific values, in which case those values are listed in<>, separated by|.
- _<suffix>means that there are several (>6) valid suffixes for this filename pattern.
- .<extension>means that there are several (>6) valid extensions for this file type.
- [.gz]means that both the unzipped and gzipped versions of the extension are valid.

Required fields:

Key name Requirement Level Data type Description

Units REQUIRED string Measurement units for the associated
file. SI units in CMIXF formatting are
RECOMMENDED (see Units).
Fieldmaps must be in units of Hertz
("Hz"), radians per second ("rad/s"), or
Tesla ("T").

For example:

{
"Units": "rad/s",
"IntendedFor":"bids::sub-01/func/sub-01_task-motor_bold.nii.gz",
"B0FieldIdentifier": "b0map_fmap0"
}

See UsingIntendedFormetadata for details on theIntendedForfield.

Case 4: Multiple phase encoded directions (”pepolar”)

Anexample datasetcontaining that type of fieldmap can be found here:

- ieeg_visual_multimodal

The phase-encoding polarity (PEpolar) technique combines two or more Spin Echo EPI scans with different phase encoding directions to estimate the distortion map
corresponding to the nonuniformities of the B0 field. These*_epi.nii[.gz]- or*_m0scan.nii[.gz]for arterial spin labeling perfusion data - files can be 3D or 4D -- in
the latter case, all timepoints share the same scanning parameters. Examples of software tools using these kinds of images are FSL TOPUP and AFNI3dqwarp.

Template:


sub-<label>/
[ses-<label>/]
fmap/
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>]_dir-<label>[_run-<index>]_epi.json
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>]_dir-<label>[_run-<index>]_epi.nii[.gz]

Legend:

- Filename entities or directories between square brackets (for example,[_ses-<label>]) are OPTIONAL.
- Some entities may only allow specific values, in which case those values are listed in<>, separated by|.
- _<suffix>means that there are several (>6) valid suffixes for this filename pattern.
- .<extension>means that there are several (>6) valid extensions for this file type.
- [.gz]means that both the unzipped and gzipped versions of the extension are valid.

Thedir-<label>entity is REQUIRED for these files. This entity MUST be used in addition to the REQUIREDPhaseEncodingDirectionmetadata field (see File name
structure).

Required fields:

Key name Requirement Level Data type Description

PhaseEncodingDirection REQUIRED string The lettersi,j,kcorrespond to the first,
second and third axis of the data in the
NIFTI file. The polarity of the phase
encoding is assumed to go from zero
index to maximum index unless-sign
is present (then the order is reversed -
starting from the highest index instead
of zero).PhaseEncodingDirectionis
defined as the direction along which
phase is was modulated which may
result in visible distortions. Note that
this is not the same as the DICOM term
InPlanePhaseEncodingDirection
which can haveROWorCOLvalues. Must
be one of:"i","j","k","i-","j-",
"k-".


Key name Requirement Level Data type Description

TotalReadoutTime REQUIRED number This is actually the ”effective” total
readout time, defined as the readout
duration, specified in seconds, that
would have generated data with the
given level of distortion. It is NOT the
actual, physical duration of the readout
train. If"EffectiveEchoSpacing"has
been properly computed, it is just
EffectiveEchoSpacing *
(ReconMatrixPE - 1).

For example:

{
"PhaseEncodingDirection": "j-",
"TotalReadoutTime":0.095,
"IntendedFor":"bids::sub-01/func/sub-01_task-motor_bold.nii.gz",
"B0FieldIdentifier": "pepolar_fmap0"
}

See UsingIntendedFormetadata for details on theIntendedForfield.

AsforotherEPIsequences,thesefieldmappingsequencesmayhaveanyofthein-planespatialencodingmetadatakeys. However,pleasenotethatPhaseEncodingDirection
andTotalReadoutTimekeys are REQUIRED for these field mapping sequences.


## Magnetoencephalography

Support for Magnetoencephalography (MEG) was developed as a BIDS Extension Proposal. Please see Citing BIDS on how to appropriately credit this extension when
referring to it in the context of the academic literature.

The following example MEG datasets have been formatted using this specification and can be used for practical guidance when curating a new dataset.

- multimodal MEG and MRI

Further datasets are available from theBIDS examples repository.

### MEG recording data

Template:

sub-<label>/
[ses-<label>/]
meg/
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>][_proc-<label>][_split-<index>]_meg.<extension>
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>][_proc-<label>][_split-<index>]_meg.json
sub-<label>[_ses-<label>]_acq-<calibration>_meg.dat
sub-<label>[_ses-<label>]_acq-<crosstalk>_meg.fif
sub-<label>[_ses-<label>][_task-<label>][_acq-<label>][_space-<label>]_markers.mrk
sub-<label>[_ses-<label>][_task-<label>][_acq-<label>][_space-<label>]_markers.sqd
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>]_events.json
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>]_events.tsv
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>][_recording-<label>]_physio.json
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>][_recording-<label>]_physio.tsv.gz
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>][_recording-<label>]_stim.json
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>][_recording-<label>]_stim.tsv.gz

Legend:


- Filename entities or directories between square brackets (for example,[_ses-<label>]) are OPTIONAL.
- Some entities may only allow specific values, in which case those values are listed in<>, separated by|.
- _<suffix>means that there are several (>6) valid suffixes for this filename pattern.
- .<extension>means that there are several (>6) valid extensions for this file type.
- [.gz]means that both the unzipped and gzipped versions of the extension are valid.

Unprocessed MEG data MUST be stored in the native file format of the MEG instrument with which the data was collected. With the MEG specification of BIDS, we wish
to promote the adoption of good practices in the management of scientific data. Hence, the emphasis is not to impose a new, generic data format for the modality, but
rather to standardize the way data is stored in repositories. Further, there is currently no widely accepted standard file format for MEG, but major software applications,
including free and open-source solutions for MEG data analysis, provide readers of such raw files.

Some software readers may skip important metadata that is specific to MEG system manufacturers. It is therefore RECOMMENDED that users provide additional meta
information extracted from the manufacturer raw data files in a sidecar JSON file. This allows for easy searching and indexing of key metadata elements without the
need to parse files in proprietary data format. Other relevant files MAY be included alongside the MEG data; examples are provided below.

This template is for MEG data of any kind, including but not limited to task-based, resting-state, and noise recordings. If multiple Tasks were performed within a single
Run, the task description can be set totask-multitask. The*_meg.jsonfile SHOULD contain details on the Tasks.

Some manufacturers’ data storage conventions use directories which contain data files of various nature: for example, CTF’s.dsformat, or BTi/4D’s data directory. Yet
other manufacturers split their files once they exceed a certain size limit. For example Neuromag/Elekta/Megin, which can produce several files for a single recording.
Bothsome_file.fifandsome_file-1.fifwouldbelongtoasinglerecording. InBIDS,thesplitentityisRECOMMENDEDtodealwithsplitfiles. Iftherearemultiple
parts of a recording and the optionalscans.tsvis provided, remember to list all files separately inscans.tsvand that the entries for theacq_timecolumn inscans.tsv
MUST all be identical, as described in Scans file.

Another manufacturer-specific detail pertains to the KIT/Yokogawa/Ricoh system, which saves the MEG sensor coil positions in a separate file with two possible filename
extensions (.sqd,.mrk). For these files, themarkerssuffix MUST be used. For example:sub-01_task-nback_markers.sqd

Please refer to the MEG File Formats Appendix for general information on how to deal with such manufacturer specifics and to see more examples.

Theproc-<label>entityisanalogoustotherec-<label>entityforMRI,anddenotesavariantofafilethatwasaresultofparticularprocessingperformedonthedevice.
This is useful for files produced in particular by Elekta’s MaxFilter (for example, sss, tsss, trans, quat, mc), which some installations impose to be run on raw data prior to
analysis. SuchprocessingstepsareneededforexamplebecauseofactiveshieldingsoftwarecorrectionsthathavetobeperformedtobeforetheMEGdatacanactuallybe
exploited.

#### Recording EEG simultaneously with MEG.

Note that if EEG is recorded with a separate amplifier, it SHOULD be stored separately under a new/eegdata type (see the EEG specification).

If however EEG is recorded simultaneously with the same MEG system, it MAY be stored under the/megdata type. In that case, it SHOULD have the same sampling
frequency as MEG (seeSamplingFrequencyfield below). Furthermore, the EEG sensor coordinates SHOULD be specified using MEG-specific coordinate systems (see
coordinates section below and the Coordinate Systems Appendix).

#### Sidecar JSON (*_meg.json)

Generic fields MUST be present:


Key name Requirement Level Data type Description

TaskName REQUIRED string Name of the task. No two tasks should
have the same name. The task label
included in the file name is derived from
this"TaskName"field by removing all
non-alphanumeric characters (that is,
all except those matching
[0-9a-zA-Z]). For example
"TaskName" "faces n-back"will
correspond to task labelfacesnback. A
RECOMMENDED convention is to
name resting state task using labels
beginning withrest.

SHOULDbepresent: Forconsistencybetweenstudiesandinstitutions,weencourageuserstoextractthevaluesofthesefieldsfromtheactualrawdata. Wheneverpossible,
please avoid using ad-hoc wording.

Key name Requirement Level Data type Description

InstitutionName RECOMMENDED string The name of the institution in charge of
the equipment that produced the
measurements.
InstitutionAddress RECOMMENDED string The address of the institution in charge
of the equipment that produced the
measurements.
InstitutionalDepartmentName RECOMMENDED string The department in the institution in
charge of the equipment that produced
the measurements.
Manufacturer RECOMMENDED string Manufacturer of the equipment that
produced the measurements. For MEG
scanners, this must be one of:"CTF",
"Elekta/Neuromag","BTi/4D",
"KIT/Yokogawa","ITAB","KRISS",
"Other". See the Manufacturer for
preferred names.


Key name Requirement Level Data type Description

ManufacturersModelName RECOMMENDED string Manufacturer’s model name of the
equipment that produced the
measurements. See the
ManufacturersModelName for
preferred names.
SoftwareVersions RECOMMENDED string Manufacturer’s designation of software
version of the equipment that produced
the measurements.
TaskDescription RECOMMENDED string Longer description of the task.
Instructions RECOMMENDED string Text of the instructions given to
participants before the recording. This
is especially important in context of
resting state recordings and
distinguishing between eyes open and
eyes closed paradigms.
CogAtlasID RECOMMENDED string CogAtlasID of the corresponding
Cognitive AtlasTask term.
CogPOID RECOMMENDED string CogPOID of the correspondingCogPO
term.
DeviceSerialNumber RECOMMENDED string The serial number of the equipment
that produced the measurements. A
pseudonym can also be used to prevent
the equipment from being identifiable,
so long as each pseudonym is unique
within the dataset.

Specific MEG fields MUST be present:

Key name Requirement Level Data type Description

SamplingFrequency REQUIRED number Sampling frequency (in Hz) of all the
data in the recording, regardless of their
type (for example, 2400 ). The sampling
frequency of data channels that deviate
from the main sampling frequency
SHOULD be specified in the
channels.tsvfile.


Key name Requirement Level Data type Description

PowerLineFrequency REQUIRED numberor"n/a" Frequency (in Hz) of the power grid at
the geographical location of the
instrument (for example, 50 or 60 ).
DewarPosition REQUIRED string Position of the dewar during the MEG
scan:"upright","supine"or
"degrees"of angle from vertical: for
example on CTF systems,
"upright=15°, supine=90°".
SoftwareFilters REQUIRED objectofobjectsor"n/a" Objectof temporal software filters
applied, or"n/a"if the data is not
available. Each key-value pair in the
JSON object is a name of the filter and
an object in which its parameters are
defined as key-value pairs (for example,
{"Anti-aliasing filter":
{"half-amplitude cutoff (Hz)":
500, "Roll-off": "6dB/Octave"}}).
DigitizedLandmarks REQUIRED boolean trueorfalsevalue indicating whether
anatomical landmark points (fiducials)
are contained within this recording.
Must be one of:"true","false".
DigitizedHeadPoints REQUIRED boolean trueorfalsevalue indicating whether
head points outlining the scalp/face
surface are contained within this
recording. Must be one of:"true",
"false".

SHOULD be present:

Key name Requirement Level Data type Description

MEGChannelCount RECOMMENDED integer Number of MEG channels (for example,
275 ). Must be a number greater than or
equal to 0.


Key name Requirement Level Data type Description

MEGREFChannelCount RECOMMENDED integer Number of MEG reference channels (for
example, 23 ). For systems without such
channels (for example, Neuromag
Vectorview),MEGREFChannelCount
should be set to 0. Must be a number
greater than or equal to 0.
EEGChannelCount RECOMMENDED integer Number of EEG channels recorded
simultaneously (for example, 21 ). Must
be a number greater than or equal to 0.
ECOGChannelCount RECOMMENDED integer Number of ECoG channels. Must be a
number greater than or equal to 0.
SEEGChannelCount RECOMMENDED integer Number of SEEG channels. Must be a
number greater than or equal to 0.
EOGChannelCount RECOMMENDED integer Number of EOG channels. Must be a
number greater than or equal to 0.
ECGChannelCount RECOMMENDED integer Number of ECG channels. Must be a
number greater than or equal to 0.
EMGChannelCount RECOMMENDED integer Number of EMG channels. Must be a
number greater than or equal to 0.
MiscChannelCount RECOMMENDED integer Number of miscellaneous analog
channels for auxiliary signals. Must be
a number greater than or equal to 0.
TriggerChannelCount RECOMMENDED integer Number of channels for digital (TTL bit
level) triggers. Must be a number
greater than or equal to 0.
RecordingDuration RECOMMENDED number Length of the recording in seconds (for
example, 3600 ).
RecordingType RECOMMENDED string Defines whether the recording is
"continuous","discontinuous", or
"epoched", where"epoched"is limited
to time windows about events of
interest (for example, stimulus
presentations or subject responses).
Must be one of:"continuous",
"epoched","discontinuous".


Key name Requirement Level Data type Description

EpochLength RECOMMENDED number Duration of individual epochs in
seconds (for example, 1 ) in case of
epoched data. If recording was
continuous or discontinuous, leave out
the field. Must be a number greater
than or equal to 0.
ContinuousHeadLocalization RECOMMENDED boolean trueorfalsevalue indicating whether
continuous head localisation was
performed. Must be one of:"true",
"false".
HeadCoilFrequency RECOMMENDED numberorarrayofnumbers List of frequencies (in Hz) used by the
head localisation coils (’HLC’ in CTF
systems, ’HPI’ in Elekta, ’COH’ in
BTi/4D) that track the subject’s head
position in the MEG helmet (for
example,[293, 307, 314, 321]).
MaxMovement RECOMMENDED number Maximum head movement (in mm)
detected during the recording, as
measured by the head localisation coils
(for example,4.8).
SubjectArtefactDescription RECOMMENDED string Freeform description of the observed
subject artefact and its possible cause
(for example,"Vagus Nerve
Stimulator","non-removable
implant"). If this field is set to"n/a", it
will be interpreted as absence of major
source of artifacts except cardiac and
blinks.
AssociatedEmptyRoom RECOMMENDED arrayorstring One or more AssociatedEmptyRoom
pointing to empty-room file(s)
associated with the subject’s MEG
recording. Using forward-slash
separated paths relative to the dataset
root is AssociatedEmptyRoom.


Key name Requirement Level Data type Description

HardwareFilters RECOMMENDED objectofobjectsor"n/a" Object of temporal hardware filters
applied, or"n/a"if the data is not
available. Each key-value pair in the
JSON object is a name of the filter and
an object in which its parameters are
defined as key-value pairs. For example,
{"Highpass RC filter": {"Half
amplitude cutoff (Hz)": 0.0159,
"Roll-off": "6dB/Octave"}}.

Specific EEG fields (if recorded with MEG, see Recording EEG simultaneously with MEG SHOULD be present:

Key name Requirement Level Data type Description

EEGPlacementScheme OPTIONAL string Placement scheme of EEG electrodes.
Either the name of a standardized
placement system (for example,
"10-20") or a list of standardized
electrode names (for example,["Cz",
"Pz"]).
CapManufacturer OPTIONAL string Name of the cap manufacturer (for
example,"EasyCap").
CapManufacturersModelName OPTIONAL string Manufacturer’s designation of the cap
model (for example,"actiCAP 64 Ch
Standard-2").
EEGReference OPTIONAL string General description of the reference
scheme used and (when applicable) of
location of the reference electrode in the
raw recordings (for example,"left
mastoid","Cz","CMS"). If different
channels have a different reference, this
field should have a general description
and the channel specific reference
should be defined in thechannels.tsv
file.


Example ***_meg.json**

{
"InstitutionName":"Stanford University",
"InstitutionAddress": "450 Serra Mall, Stanford, CA 94305-2004, USA",
"Manufacturer":"CTF",
"ManufacturersModelName": "CTF-275",
"DeviceSerialNumber": "11035",
"SoftwareVersions":"Acq 5.4.2-linux-20070507",
"PowerLineFrequency": 60 ,
"SamplingFrequency": 2400 ,
"MEGChannelCount": 270 ,
"MEGREFChannelCount": 26 ,
"EEGChannelCount": 0 ,
"EOGChannelCount": 2 ,
"ECGChannelCount": 1 ,
"EMGChannelCount": 0 ,
"DewarPosition":"upright",
"SoftwareFilters":{
"SpatialCompensation":{"GradientOrder": "3rd"}
},
"RecordingDuration": 600 ,
"RecordingType": "continuous",
"EpochLength": 0 ,
"TaskName":"rest",
"ContinuousHeadLocalization": **true** ,
"HeadCoilFrequency": [ 1470 , 1530 , 1590 ],
"DigitizedLandmarks": **true** ,
"DigitizedHeadPoints": **true**
}

Note that the date and time information SHOULD be stored in the Study key file (scans.tsv), see Scans file. Date time information MUST be expressed as indicated in
Units

### Channels description (*_channels.tsv)

Template:

sub-<label>/
[ses-<label>/]
meg/


```
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>][_proc-<label>]_channels.json
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>][_proc-<label>]_channels.tsv
```
Legend:

- Filename entities or directories between square brackets (for example,[_ses-<label>]) are OPTIONAL.
- Some entities may only allow specific values, in which case those values are listed in<>, separated by|.
- _<suffix>means that there are several (>6) valid suffixes for this filename pattern.
- .<extension>means that there are several (>6) valid extensions for this file type.
- [.gz]means that both the unzipped and gzipped versions of the extension are valid.

ThisfileisRECOMMENDEDasitprovideseasilysearchableinformationacrossBIDSdatasets. Forexampleforgeneralcuration,responsetoqueries,orforbatchanalysis.
Toavoidconfusion,thechannelsSHOULDbelistedintheordertheyappearintheMEGdatafile. AnynumberofadditionalcolumnsMAYbeaddedtoprovideadditional
information about the channels. Missing values MUST be indicated with"n/a".

The columns of the channels description table stored in*_channels.tsvare:

Column name Requirement Level Data type Description

name REQUIRED string Label of the channel. Values inname
MUST be unique.This column must
appear first in the file.
type REQUIRED string Type of channel; MUST use the channel
types listed below. Note that the type
MUST be in upper-case. This column
must appear second in the file.For a list
of valid values for this column, see the
type.
units REQUIRED string Physical unit of the value represented
in this channel, for example,Vfor Volt,
orfT/cmfor femto Tesla per centimeter
(see units). This column must appear
third in the file.
description OPTIONAL string Brief free-text description of the
channel, or other information of
interest. This column may appear
anywhere in the file.
sampling_frequency OPTIONAL number Sampling rate of the channel in Hz.
This column may appear anywhere in
the file.


Column name Requirement Level Data type Description

low_cutoff OPTIONAL numberor"n/a" Frequencies used for the high-pass filter
applied to the channel in Hz. If no
high-pass filter applied, usen/a. This
column may appear anywhere in the
file.
high_cutoff OPTIONAL numberor"n/a" Frequencies used for the low-pass filter
applied to the channel in Hz. If no
low-pass filter applied, usen/a. Note
that hardware anti-aliasing in A/D
conversion of all MEG/EEG electronics
applies a low-pass filter; specify its
frequency here if applicable. This
column may appear anywhere in the
file.
notch OPTIONAL numberor"n/a" Frequencies used for the notch filter
applied to the channel, in Hz. If no
notch filter applied, usen/a. This
column may appear anywhere in the
file.
software_filters OPTIONAL stringor"n/a" List of temporal and/or spatial software
filters applied (for example,SSS,
SpatialCompensation). Note that
parameters should be defined in the
general MEG sidecar .json file. Indicate
n/ain the absence of software filters
applied. This column may appear
anywhere in the file.
status OPTIONAL string Data quality observed on the channel.
A channel is consideredbadif its data
quality is compromised by excessive
noise. If quality is unknown, then a
value ofn/amay be used. Description
of noise type SHOULD be provided in
[status_description]. This column
may appear anywhere in the file.Must
be one of:"good","bad","n/a".


Column name Requirement Level Data type Description

status_description OPTIONAL string Freeform text description of noise or
artifact affecting data quality on the
channel. It is meant to explain why the
channel was declared bad in thestatus
column. This column may appear
anywhere in the file.
Additional Columns OPTIONAL n/a Additional columns are allowed if they
are defined in the associated metadata
file.

Example:

name type units description sampling_frequency low_cutoff high_cutoff notch software_filters status
UDIO001 TRIG V analogue trigger 1200 0.1 300 0 n/a good
MLC11 MEGGRADAXIAL T sensor 1st-order grad 1200 0 n/a 50 SSS bad

Restricted keyword list for fieldtype. Note that upper-case is REQUIRED:

```
Keyword Description
MEGMAG MEG magnetometer
MEGGRADAXIAL MEG axial gradiometer
MEGGRADPLANAR MEG planargradiometer
MEGREFMAG MEG reference magnetometer
MEGREFGRADAXIAL MEG reference axial gradiometer
MEGREFGRADPLANAR MEG reference planar gradiometer
MEGOTHER Any other type of MEG sensor
EEG Electrode channel
ECOG Electrode channel
SEEG Electrode channel
DBS Electrode channel
VEOG Vertical EOG (electrooculogram)
HEOG Horizontal EOG
EOG Generic EOG channel
ECG ElectroCardioGram (heart)
EMG ElectroMyoGram (muscle)
TRIG System Triggers
AUDIO Audio signal
PD Photodiode
```

```
Keyword Description
EYEGAZE Eye Tracker gaze
PUPIL Eye Tracker pupil diameter
MISC Miscellaneous
SYSCLOCK System time showing elapsed time since trial started
ADC Analog to Digital input
DAC Digital to Analog output
HLU Measured position of head and head coils
FITERR Fit error signal from each head localization coil
OTHER Any other type of channel
```
Examples of free text for fielddescription:

- stimulus
- response
- vertical EOG
- horizontal EOG
- skin conductance
- sats
- intracranial
- eyetracker

#### Example*_channels.tsv.

name type units description
VEOG VEOG V vertical EOG
FDI EMG V left first dorsal interosseous
UDIO001 TRIG V analog trigger signal
UADC001 AUDIO V envelope of audio signal presented to participant

### Coordinate System JSON (*_coordsystem.json)

Template:

sub-<label>/
[ses-<label>/]
meg/
sub-<label>[_ses-<label>][_acq-<label>]_coordsystem.json

Legend:


- Filename entities or directories between square brackets (for example,[_ses-<label>]) are OPTIONAL.
- Some entities may only allow specific values, in which case those values are listed in<>, separated by|.
- _<suffix>means that there are several (>6) valid suffixes for this filename pattern.
- .<extension>means that there are several (>6) valid extensions for this file type.
- [.gz]means that both the unzipped and gzipped versions of the extension are valid.

OPTIONAL. A JSON document specifying the coordinate system(s) used for the MEG, EEG, head localization coils, and anatomical landmarks.

MEG and EEG sensors:

Key name Requirement Level Data type Description

MEGCoordinateSystem REQUIRED string Defines the coordinate system for the
MEG sensors. See the
MEGCoordinateSystem for a list of
restricted keywords for coordinate
systems. If"Other", provide definition
of the coordinate system in
"MEGCoordinateSystemDescription".
For a list of valid values for this field,
see the MEGCoordinateSystem.
MEGCoordinateUnits REQUIRED string Units of the coordinates of
"MEGCoordinateSystem". Must be one
of:"m","mm","cm","n/a".
MEGCoordinateSystemDescription OPTIONAL, but REQUIRED if
MEGCoordinateSystemisOther

```
string Free-form text description of the
coordinate system. May also include a
link to a documentation page or paper
describing the system in greater detail.
```

Key name Requirement Level Data type Description

EEGCoordinateSystem OPTIONAL string Defines the coordinate system for the
EEG sensors.See the
EEGCoordinateSystem for a list of
restricted keywords for coordinate
systems. If"Other", provide definition
of the coordinate system in
EEGCoordinateSystemDescription.
See [Recording EEG simultaneously
with MEG]
(/04-modality-specific-files/02-
magnetoencephalography.html#recording-
eeg-simultaneously-with-meg).
Preferably the same as the
MEGCoordinateSystem. For a list of
valid values for this field, see the
EEGCoordinateSystem.
EEGCoordinateUnits OPTIONAL string Units of the coordinates of
EEGCoordinateSystem. Must be one of:
"m","mm","cm","n/a".
EEGCoordinateSystemDescription OPTIONAL, but REQUIRED if
EEGCoordinateSystemisOther

```
string Free-form text description of the
coordinate system. May also include a
link to a documentation page or paper
describing the system in greater detail.
See [Recording EEG simultaneously
with MEG]
(/04-modality-specific-files/02-
magnetoencephalography.html#recording-
eeg-simultaneously-with-meg).
```
Head localization coils:


Key name Requirement Level Data type Description

HeadCoilCoordinates OPTIONAL objectofarrays Key-value pairs describing head
localization coil labels and their
coordinates, interpreted following the
HeadCoilCoordinateSystem(for
example,{"NAS": [12.7,21.3,13.9],
"LPA": [5.2,11.3,9.6], "RPA":
[20.2,11.3,9.1]}). Note that coils are
not always placed at locations that
have a known anatomical name (for
example, for Elekta, Yokogawa
systems); in that case generic labels can
be used (for example,{"coil1":
[12.2,21.3,12.3], "coil2":
[6.7,12.3,8.6], "coil3":
[21.9,11.0,8.1]}). Each array MUST
contain three numeric values
corresponding to x, y, and z axis of the
coordinate system in that exact order.
HeadCoilCoordinateSystem OPTIONAL string Defines the coordinate system for the
head coils. See the
HeadCoilCoordinateSystem for a list of
restricted keywords for coordinate
systems. If"Other", provide definition
of the coordinate system in
HeadCoilCoordinateSystemDescription.
For a list of valid values for this field,
see the HeadCoilCoordinateSystem.
HeadCoilCoordinateUnits OPTIONAL string Units of the coordinates of
HeadCoilCoordinateSystem. Must be
one of:"m","mm","cm","n/a".
HeadCoilCoordinateSystemDescription OPTIONAL, but REQUIRED if
HeadCoilCoordinateSystemisOther

```
string Free-form text description of the
coordinate system. May also include a
link to a documentation page or paper
describing the system in greater detail.
```
Digitized head points:


Key name Requirement Level Data type Description

DigitizedHeadPoints OPTIONAL boolean trueorfalsevalue indicating whether
head points outlining the scalp/face
surface are contained within this
recording. Must be one of:"true",
"false".
DigitizedHeadPointsCoordinateSystem OPTIONAL string Defines the coordinate system for the
digitized head points. See the
DigitizedHeadPointsCoordinateSystem
for a list of restricted keywords for
coordinate systems. If"Other", provide
definition of the coordinate system in
"DigitizedHeadPointsCoordinateSystemDescription".
For a list of valid values for this field,
see the
DigitizedHeadPointsCoordinateSystem.
DigitizedHeadPointsCoordinateUnits OPTIONAL string Units of the coordinates of
"DigitizedHeadPointsCoordinateSystem".
Must be one of:"m","mm","cm","n/a".
DigitizedHeadPointsCoordinateSystemDescriptionOPTIONAL, but REQUIRED if
DigitizedHeadPointsCoordinateSystem
isOther

```
string Free-form text description of the
coordinate system. May also include a
link to a documentation page or paper
describing the system in greater detail.
```
Anatomical MRI:

Key name Requirement Level Data type Description

IntendedFor OPTIONAL stringorarray The paths to files for which the
associated file is intended to be used.
Contains one or more IntendedFor.
Using forward-slash separated paths
relative to the participant subdirectory
is IntendedFor. This is used to identify
the structural MRI(s), possibly of
different types if a list is specified, to be
used with the MEG recording.

Anatomical landmarks:


Key name Requirement Level Data type Description

AnatomicalLandmarkCoordinates OPTIONAL objectofarrays Key-value pairs of the labels and 3-D
digitized locations of anatomical
landmarks, interpreted following the
"AnatomicalLandmarkCoordinateSystem"
(for example,{"NAS":
[12.7,21.3,13.9], "LPA":
[5.2,11.3,9.6], "RPA":
[20.2,11.3,9.1]}. Each array MUST
contain three numeric values
corresponding to x, y, and z axis of the
coordinate system in that exact order.
AnatomicalLandmarkCoordinateSystem OPTIONAL string Defines the coordinate system for the
anatomical landmarks. See the Anatom-
icalLandmarkCoordinateSystem for a
list of restricted keywords for
coordinate systems. If"Other", provide
definition of the coordinate system in
"AnatomicalLandmarkCoordinateSystemDescription".
Preferably the same as the
MEGCoordinateSystem. For a list of
valid values for this field, see the
AnatomicalLandmarkCoordinateSys-
tem.
AnatomicalLandmarkCoordinateUnits OPTIONAL string Units of the coordinates of
"AnatomicalLandmarkCoordinateSystem".
Must be one of:"m","mm","cm","n/a".
AnatomicalLandmarkCoordinateSystemDescriptionOPTIONAL, but REQUIRED if
AnatomicalLandmarkCoordinateSystem
isOther

```
string Free-form text description of the
coordinate system. May also include a
link to a documentation page or paper
describing the system in greater detail.
```
It is also RECOMMENDED that the MRI voxel coordinates of the actual anatomical landmarks for co-registration of MEG with structural MRI are stored in the
AnatomicalLandmarkCoordinatesfieldintheJSONsidecarofthecorrespondingT1wMRIanatomicaldataofthesubjectseenintheMEGsession(seeAnatomyImaging
Data).

For example:"sub-01/ses-mri/anat/sub-01_ses-mri_acq-mprage_T1w.json"

In principle, these locations are those of absolute anatomical markers. However, the marking of NAS, LPA and RPA is more ambiguous than that of for example, AC and
PC. This may result in some variability in their 3-D digitization from session to session, even for the same participant. The solution would be to use only one T1w file and


populate theAnatomicalLandmarkCoordinatesfield with session-specific labels for example, ”NAS-session1”:[127,213,139],”NAS-session2”:[123,220,142].

Fiducials information:

Key name Requirement Level Data type Description

FiducialsDescription OPTIONAL string Free-form text description of how the
fiducials such as vitamin-E capsules
were placed relative to anatomical
landmarks, and how the position of the
fiducials were measured (for example,
"both with Polhemus and with T1w
MRI").

For more information on the definition of anatomical landmarks, please visit:http://www.fieldtriptoolbox.org/faq/how_are_the_lpa_and_rpa_points_defined

For more information on typical coordinate systems for MEG-MRI coregistration:http://www.fieldtriptoolbox.org/faq/how_are_the_different_head_and_mri_coordinat
e_systems_defined, or:http://neuroimage.usc.edu/brainstorm/CoordinateSystems

### Landmark photos (*_photo.jpg).

Photos of the anatomical landmarks and/or head localization coils (*_photo.jpg)

Template:

sub-<label>/
[ses-<label>/]
meg/
sub-<label>[_ses-<label>][_acq-<label>]_photo.jpg
sub-<label>[_ses-<label>][_acq-<label>]_photo.png
sub-<label>[_ses-<label>][_acq-<label>]_photo.tif

Legend:

- Filename entities or directories between square brackets (for example,[_ses-<label>]) are OPTIONAL.
- Some entities may only allow specific values, in which case those values are listed in<>, separated by|.
- _<suffix>means that there are several (>6) valid suffixes for this filename pattern.
- .<extension>means that there are several (>6) valid extensions for this file type.
- [.gz]means that both the unzipped and gzipped versions of the extension are valid.

Photosoftheanatomicallandmarksand/orheadlocalizationcoilsonthesubject’sheadareRECOMMENDED.Ifthecoilsarenotplacedatthelocationofactualanatomical
landmarks, these latter may be marked with a piece of felt-tip taped to the skin. Please note that the photos may need to be cropped or blurred to conceal identifying
features prior to sharing, depending on the terms of the consent given by the participant.


Theacq-<label>entity can be used to indicate acquisition of different photos of the same face (or other body part in different angles to show, for example, the location
of the nasion (NAS) as opposed to the right periauricular point (RPA)).

#### Example*_photo.jpg.

Example of the NAS fiducial placed between the eyebrows, rather than at the actual anatomical nasion:sub-0001_ses-001_acq-NAS_photo.jpg

### Head shape and electrode description (*_headshape.<ext>).

Template:

sub-<label>/
[ses-<label>/]
meg/
sub-<label>[_ses-<label>][_acq-<label>]_headshape.*
sub-<label>[_ses-<label>][_acq-<label>]_headshape.pos

Legend:

- Filename entities or directories between square brackets (for example,[_ses-<label>]) are OPTIONAL.
- Some entities may only allow specific values, in which case those values are listed in<>, separated by|.
- _<suffix>means that there are several (>6) valid suffixes for this filename pattern.
- .<extension>means that there are several (>6) valid extensions for this file type.
- [.gz]means that both the unzipped and gzipped versions of the extension are valid.


This file is RECOMMENDED.

The 3-D locations of points that describe the head shape and/or EEG electrode locations can be digitized and stored in separate files. Theacq-<label>entity can be used
when more than one type of digitization in done for a session, for example when the head points are in a separate file from the EEG locations. These files are stored in the
specific format of the 3-D digitizer’s manufacturer (see the MEG File Formats Appendix).

For example:

```
sub-control01/
ses-01/
sub-control01_ses-01_acq-HEAD_headshape.pos
sub-control01_ses-01_acq-EEG_headshape.pos
```
Note that the*_headshapefile(s) is shared by all the runs and tasks in a session. If the subject needs to be taken out of the scanner and the head-shape has to be updated,
then for MEG it could be considered to be a new session.

### Empty-room MEG recordings.

Empty-room MEG recordings capture the environmental and recording system’s noise.

It is RECOMMENDED to explicitly specify which empty-room recording should be used with which experimental run(s) or session(s). This can be done via the
AssociatedEmptyRoomfield in the*_meg.jsonsidecar files.

Empty-room recordings may be collected once per day, where a single empty-room recording may be shared between multiple subjects and/or sessions (see Example 1).
Empty-room recordings can also be collected for each individual experimental session (see Example 2).

In the case of empty-room recordings being associated with multiple subjects and/or sessions, it is RECOMMENDED to store the empty-room recording inside a subject
directory namedsub-emptyroom. If asession-<label>entity is present, its label SHOULD be the date of the empty-room recording in the formatYYYYMMDD, that is
ses-YYYYMMDD. Thescans.tsvfile containing the date and time of the acquisition SHOULD also be included. The rationale is that this naming scheme will allow users
to easily retrieve the empty-room recording that best matches a particular experimental session, based on date and time of the recording. It should be possible to query
empty-room recordings just like usual subject recordings, hence all metadata sidecar files (such as thechannels.tsv) file SHOULD be present as well.

Inthecaseofempty-roomrecordingsbeingcollectedfortheindividualexperimentalsession,itisrecommendedtostoretheempty-roomrecordingalongwiththatsubject
and session.

In either case, the label for thetask-<label>entity in the empty-room recording SHOULD be set tonoise.

#### Example 1.

One empty-room recording per day, applying to all subjects for that day.

```
sub-control01/
sub-control02/
sub-emptyroom/
ses-20170801/
```

```
sub-emptyroom_ses-20170801_scans.tsv
meg/
sub-emptyroom_ses-20170801_task-noise_meg.ds
sub-emptyroom_ses-20170801_task-noise_meg.json
sub-emptyroom_ses-20170801_task-noise_channels.tsv
```
#### Example 2.

One recording per session, stored within the session directory.

```
sub-control01/
ses-01/
sub-01_ses-01_scans.tsv
meg/
sub-control01_ses-01_task-rest_meg.ds
sub-control01_ses-01_task-rest_meg.json
sub-control01_ses-01_task-rest_channels.tsv
sub-control01_ses-01_task-noise_meg.ds
sub-control01_ses-01_task-noise_meg.json
sub-control01_ses-01_task-noise_channels.tsv
```

## Electroencephalography

Support for Electroencephalography (EEG) was developed as a BIDS Extension Proposal. Please see Citing BIDS on how to appropriately credit this extension when
referring to it in the context of the academic literature.

Severalexample EEG datasetshave been formatted using this specification and can be used for practical guidance when curating a new dataset.

### EEG recording data

Template:

sub-<label>/
[ses-<label>/]
eeg/
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>]_eeg.<extension>
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>]_eeg.json
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>]_events.json
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>]_events.tsv
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>][_recording-<label>]_physio.json
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>][_recording-<label>]_physio.tsv.gz
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>][_recording-<label>]_stim.json
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>][_recording-<label>]_stim.tsv.gz

Legend:

- Filename entities or directories between square brackets (for example,[_ses-<label>]) are OPTIONAL.
- Some entities may only allow specific values, in which case those values are listed in<>, separated by|.
- _<suffix>means that there are several (>6) valid suffixes for this filename pattern.
- .<extension>means that there are several (>6) valid extensions for this file type.
- [.gz]means that both the unzipped and gzipped versions of the extension are valid.


The EEG community uses a variety of formats for storing raw data, and there is no single standard that all researchers agree on. For BIDS, EEG data MUST be stored in
one of the following formats:

```
Format Extension(s) Description
European data format .edf Each recording consists of a single.edffile.edf+files
are permitted. The capital.EDFextension MUST
NOT be used.
BrainVision Core Data Format .vhdr,.vmrk,.eeg Each recording consists of a.vhdr,.vmrk,.eegfile
triplet.
EEGLAB .set,.fdt The format used by the MATLAB toolboxEEGLAB.
Each recording consists of a.setfile with an
OPTIONAL.fdtfile.
Biosemi .bdf Each recording consists of a single.bdffile.bdf+files
are permitted. The capital.BDFextension MUST
NOT be used.
```
It is RECOMMENDED to use the European data format, or the BrainVision data format. It is furthermore discouraged to use the other accepted formats over these
RECOMMENDED formats, particularly because there are conversion scripts available in most commonly used programming languages to convert data into the RECOM-
MENDED formats. The data in their original format, if different from the supported formats, can be stored in the/sourcedatadirectory.

TheoriginaldataformatisespeciallyvaluableincaseconversionelicitsthelossofcrucialmetadataspecifictomanufacturersandspecificEEGsystems. Wealsoencourage
users to provide additional meta information extracted from the manufacturer specific data files in the sidecar JSON file. Other relevant files MAY be included alongside
the original EEG data in/sourcedata.

Note theRecordingType, which depends on whether the data stream on disk is interrupted or not. Continuous data is by definition 1 segment without interruption.
Epoched data consists of multiple segments that all have the same length (for example, corresponding to trials) and that have gaps in between. Discontinuous data
consists of multiple segments of different length, for example due to a pause in the acquisition.

NotethatforproperdocumentationofEEGrecordingmetadataitisimportanttounderstandthedifferencebetweenelectrodeandchannel: AnEEGelectrodeisattached
to the skin, whereas a channel is the combination of the analog differential amplifier and analog-to-digital converter that result in a potential (voltage) difference that is
stored in the EEG dataset. We employ the following short definitions:

- Electrode=Asinglepointofcontactbetweentheacquisitionsystemandtherecordingsite(forexample,scalp,neuraltissue,...). Multipleelectrodescanbeorganized
    as caps (for EEG), arrays, grids, leads, strips, probes, shafts, and so on.
- Channel=Asingleanalog-to-digitalconverterintherecordingsystemthatregularlysamplesthevalueofatransducer,whichresultsinthesignalbeingrepresented
    asatimeseriesinthedigitizeddata. Thiscanbeconnectedtotwoelectrodes(tomeasurethepotentialdifferencebetweenthem),amagneticfieldormagneticgradient
    sensor, temperature sensor, accelerometer, and so on.

Although the reference and ground electrodes are often referred to as channels, they are in most common EEG systems not recorded by themselves. Therefore they are
not represented as channels in the data. The type of referencing for all channels and optionally the location of the reference electrode and the location of the ground
electrode MAY be specified.


#### Sidecar JSON (*_eeg.json)

Generic fields MUST be present:

Key name Requirement Level Data type Description

TaskName REQUIRED string Name of the task. No two tasks should
have the same name. The task label
included in the file name is derived from
this"TaskName"field by removing all
non-alphanumeric characters (that is,
all except those matching
[0-9a-zA-Z]). For example
"TaskName" "faces n-back"will
correspond to task labelfacesnback. A
RECOMMENDED convention is to
name resting state task using labels
beginning withrest.

SHOULDbepresent: Forconsistencybetweenstudiesandinstitutions,weencourageuserstoextractthevaluesofthesefieldsfromtheactualrawdata. Wheneverpossible,
please avoid using ad hoc wording.

Key name Requirement Level Data type Description

InstitutionName RECOMMENDED string The name of the institution in charge of
the equipment that produced the
measurements.
InstitutionAddress RECOMMENDED string The address of the institution in charge
of the equipment that produced the
measurements.
InstitutionalDepartmentName RECOMMENDED string The department in the institution in
charge of the equipment that produced
the measurements.
Manufacturer RECOMMENDED string Manufacturer of the equipment that
produced the measurements.
ManufacturersModelName RECOMMENDED string Manufacturer’s model name of the
equipment that produced the
measurements.
SoftwareVersions RECOMMENDED string Manufacturer’s designation of software
version of the equipment that produced
the measurements.


Key name Requirement Level Data type Description

TaskDescription RECOMMENDED string Longer description of the task.
Instructions RECOMMENDED string Text of the instructions given to
participants before the recording. This
is especially important in context of
resting state recordings and
distinguishing between eyes open and
eyes closed paradigms.
CogAtlasID RECOMMENDED string CogAtlasID of the corresponding
Cognitive AtlasTask term.
CogPOID RECOMMENDED string CogPOID of the correspondingCogPO
term.
DeviceSerialNumber RECOMMENDED string The serial number of the equipment
that produced the measurements. A
pseudonym can also be used to prevent
the equipment from being identifiable,
so long as each pseudonym is unique
within the dataset.

Specific EEG fields MUST be present:

Key name Requirement Level Data type Description

EEGReference REQUIRED string General description of the reference
scheme used and (when applicable) of
location of the reference electrode in the
raw recordings (for example,"left
mastoid","Cz","CMS"). If different
channels have a different reference, this
field should have a general description
and the channel specific reference
should be defined in thechannels.tsv
file.


Key name Requirement Level Data type Description

SamplingFrequency REQUIRED number Sampling frequency (in Hz) of all the
data in the recording, regardless of their
type (for example, 2400 ). The sampling
frequency of data channels that deviate
from the main sampling frequency
SHOULD be specified in the
channels.tsvfile.
PowerLineFrequency REQUIRED numberor"n/a" Frequency (in Hz) of the power grid at
the geographical location of the
instrument (for example, 50 or 60 ).
SoftwareFilters REQUIRED objectofobjectsor"n/a" Objectof temporal software filters
applied, or"n/a"if the data is not
available. Each key-value pair in the
JSON object is a name of the filter and
an object in which its parameters are
defined as key-value pairs (for example,
{"Anti-aliasing filter":
{"half-amplitude cutoff (Hz)":
500, "Roll-off": "6dB/Octave"}}).

SHOULD be present:

Key name Requirement Level Data type Description

CapManufacturer RECOMMENDED string Name of the cap manufacturer (for
example,"EasyCap").
CapManufacturersModelName RECOMMENDED string Manufacturer’s designation of the cap
model (for example,"actiCAP 64 Ch
Standard-2").
EEGChannelCount RECOMMENDED integer Number of EEG channels recorded
simultaneously (for example, 21 ). Must
be a number greater than or equal to 0.
ECGChannelCount RECOMMENDED integer Number of ECG channels. Must be a
number greater than or equal to 0.
EMGChannelCount RECOMMENDED integer Number of EMG channels. Must be a
number greater than or equal to 0.
EOGChannelCount RECOMMENDED integer Number of EOG channels. Must be a
number greater than or equal to 0.


Key name Requirement Level Data type Description

MiscChannelCount RECOMMENDED integer Number of miscellaneous analog
channels for auxiliary signals. Must be
a number greater than or equal to 0.
TriggerChannelCount RECOMMENDED integer Number of channels for digital (TTL bit
level) triggers. Must be a number
greater than or equal to 0.
RecordingDuration RECOMMENDED number Length of the recording in seconds (for
example, 3600 ).
RecordingType RECOMMENDED string Defines whether the recording is
"continuous","discontinuous", or
"epoched", where"epoched"is limited
to time windows about events of
interest (for example, stimulus
presentations or subject responses).
Must be one of:"continuous",
"epoched","discontinuous".
EpochLength RECOMMENDED number Duration of individual epochs in
seconds (for example, 1 ) in case of
epoched data. If recording was
continuous or discontinuous, leave out
the field. Must be a number greater
than or equal to 0.
EEGGround RECOMMENDED string Description of the location of the
ground electrode (for example,"placed
on right mastoid (M2)").
HeadCircumference RECOMMENDED number Circumference of the participant’s head,
expressed in cm (for example, 58 ). Must
be a number greater than 0.
EEGPlacementScheme RECOMMENDED string Placement scheme of EEG electrodes.
Either the name of a standardized
placement system (for example,
"10-20") or a list of standardized
electrode names (for example,["Cz",
"Pz"]).


Key name Requirement Level Data type Description

HardwareFilters RECOMMENDED objectofobjectsor"n/a" Object of temporal hardware filters
applied, or"n/a"if the data is not
available. Each key-value pair in the
JSON object is a name of the filter and
an object in which its parameters are
defined as key-value pairs. For example,
{"Highpass RC filter": {"Half
amplitude cutoff (Hz)": 0.0159,
"Roll-off": "6dB/Octave"}}.
SubjectArtefactDescription RECOMMENDED string Freeform description of the observed
subject artefact and its possible cause
(for example,"Vagus Nerve
Stimulator","non-removable
implant"). If this field is set to"n/a", it
will be interpreted as absence of major
source of artifacts except cardiac and
blinks.

Example ***_eeg.json**

{
"TaskName":"Seeing stuff",
"TaskDescription":"Subjects see various images for which phase, amplitude spectrum, and color vary continuously",
"Instructions":"Your task is to detect images when they appear for the 2nd time, only then press the response button with your right/left hand (counterbalanced across subjects)",
"InstitutionName":"The world best university, 10 Beachfront Avenue, Papeete",
"SamplingFrequency": 2400 ,
"Manufacturer":"Brain Products",
"ManufacturersModelName":"BrainAmp DC",
"CapManufacturer":"EasyCap",
"CapManufacturersModelName":"M1-ext",
"EEGChannelCount": 87 ,
"EOGChannelCount": 2 ,
"ECGChannelCount": 1 ,
"EMGChannelCount": 0 ,
"MiscChannelCount": 0 ,
"TriggerChannelCount": 1 ,
"PowerLineFrequency": 50 ,
"EEGPlacementScheme":"10 percent system",
"EEGReference":"single electrode placed on FCz",


"EEGGround":"placed on AFz",
"SoftwareFilters":{
"Anti-aliasing filter":{
"half-amplitude cutoff (Hz)": 500 ,
"Roll-off":"6dB/Octave"
}
},
"HardwareFilters":{
"ADC's decimation filter (hardware bandwidth limit)":{
"-3dB cutoff point (Hz)": 480 ,
"Filter order sinc response": 5
}
},
"RecordingDuration": 600 ,
"RecordingType":"continuous"
}

Note that the date and time information SHOULD be stored in the Study key file (scans.tsv). Date time information MUST be expressed as indicated in Units

### Channels description (*_channels.tsv)

Template:

sub-<label>/
[ses-<label>/]
eeg/
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>]_channels.json
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>]_channels.tsv

Legend:

- Filename entities or directories between square brackets (for example,[_ses-<label>]) are OPTIONAL.
- Some entities may only allow specific values, in which case those values are listed in<>, separated by|.
- _<suffix>means that there are several (>6) valid suffixes for this filename pattern.
- .<extension>means that there are several (>6) valid extensions for this file type.
- [.gz]means that both the unzipped and gzipped versions of the extension are valid.

ThisfileisRECOMMENDEDasitprovideseasilysearchableinformationacrossBIDSdatasets. Forexampleforgeneralcuration,responsetoqueries,orforbatchanalysis.
Toavoidconfusion,thechannelsSHOULDbelistedintheordertheyappearintheEEGdatafile. AnynumberofadditionalcolumnsMAYbeaddedtoprovideadditional
information about the channels.

Note that electrode positions SHOULD NOT be added to this file, but to*_electrodes.tsv. Furthermore, the entries in*_electrodes.tsvand*_channels.tsvdo not
have to match exactly, as for example in the case of recording a singleEOGchannel from a bipolar referencing scheme of two electrodes, or a data channel originating


from an auxiliary, non-electrode device. That is, in most cases*_electrodes.tsvwill have more entries than*_channels.tsv. See the examples for*_channels.tsv
below, and for*_electrodes.tsvin ”Electrodes description”.

The columns of the channels description table stored in*_channels.tsvare:

Column name Requirement Level Data type Description

name REQUIRED string Label of the channel. Values inname
MUST be unique.This column must
appear first in the file.
type REQUIRED string Type of channel; MUST use the channel
types listed below. Note that the type
MUST be in upper-case. This column
must appear second in the file.For a list
of valid values for this column, see the
type.
units REQUIRED string Physical unit of the value represented
in this channel, for example,Vfor Volt,
orfT/cmfor femto Tesla per centimeter
(see units). This column must appear
third in the file.
description OPTIONAL string Brief free-text description of the
channel, or other information of
interest. This column may appear
anywhere in the file.
sampling_frequency OPTIONAL number Sampling rate of the channel in Hz.
This column may appear anywhere in
the file.
reference OPTIONAL string Name of the reference electrode(s). This
column is not needed when it is
common to all channels. In that case
the reference electrode(s) can be
specified in*_eeg.jsonas
EEGReference). This column may
appear anywhere in the file.
low_cutoff OPTIONAL numberor"n/a" Frequencies used for the high-pass filter
applied to the channel in Hz. If no
high-pass filter applied, usen/a. This
column may appear anywhere in the
file.


Column name Requirement Level Data type Description

high_cutoff OPTIONAL numberor"n/a" Frequencies used for the low-pass filter
applied to the channel in Hz. If no
low-pass filter applied, usen/a. Note
that hardware anti-aliasing in A/D
conversion of all MEG/EEG electronics
applies a low-pass filter; specify its
frequency here if applicable. This
column may appear anywhere in the
file.
notch OPTIONAL numberor"n/a" Frequencies used for the notch filter
applied to the channel, in Hz. If no
notch filter applied, usen/a. This
column may appear anywhere in the
file.
status OPTIONAL string Data quality observed on the channel.
A channel is consideredbadif its data
quality is compromised by excessive
noise. If quality is unknown, then a
value ofn/amay be used. Description
of noise type SHOULD be provided in
[status_description]. This column
may appear anywhere in the file.Must
be one of:"good","bad","n/a".
status_description OPTIONAL string Freeform text description of noise or
artifact affecting data quality on the
channel. It is meant to explain why the
channel was declared bad in thestatus
column. This column may appear
anywhere in the file.
Additional Columns OPTIONAL n/a Additional columns are allowed if they
are defined in the associated metadata
file.

Restrictedkeywordlistforfieldtypeinalphabeticorder(sharedwiththeMEGandiEEGmodality;however,onlythetypesthatarecommoninEEGdataarelistedhere).
Note that upper-case is REQUIRED:


```
Keyword Description
AUDIO Audio signal
EEG Electroencephalogram channel
EOG Generic electrooculogram (eye), different from HEOG and VEOG
ECG Electrocardiogram (heart)
EMG Electromyogram (muscle)
EYEGAZE Eye tracker gaze
GSR Galvanic skin response
HEOG Horizontal EOG (eye)
MISC Miscellaneous
PPG Photoplethysmography
PUPIL Eye tracker pupil diameter
REF Reference channel
RESP Respiration
SYSCLOCK System time showing elapsed time since trial started
TEMP Temperature
TRIG System triggers
VEOG Vertical EOG (eye)
```
Examples of free-form text for fielddescription

- n/a
- stimulus
- response
- skin conductance
- battery status

#### Example*_channels.tsv.

See also the correspondingelectrodes.tsvexample.

name type units description reference status status_description
VEOG VEOG uV left eye VEOG-, VEOG+ good n/a
FDI EMG uV left first dorsal interosseous FDI-, FDI+ good n/a
Cz EEG uV n/a REF bad high frequency noise
UADC001 MISC n/a envelope of audio signal n/a good n/a

### Electrodes description (*_electrodes.tsv)

Template:


sub-<label>/
[ses-<label>/]
eeg/
sub-<label>[_ses-<label>][_acq-<label>][_space-<label>]_electrodes.json
sub-<label>[_ses-<label>][_acq-<label>][_space-<label>]_electrodes.tsv

Legend:

- Filename entities or directories between square brackets (for example,[_ses-<label>]) are OPTIONAL.
- Some entities may only allow specific values, in which case those values are listed in<>, separated by|.
- _<suffix>means that there are several (>6) valid suffixes for this filename pattern.
- .<extension>means that there are several (>6) valid extensions for this file type.
- [.gz]means that both the unzipped and gzipped versions of the extension are valid.

FilethatgivesthelocationofEEGelectrodes. NotethatcoordinatesareexpectedincartesiancoordinatesaccordingtotheEEGCoordinateSystemandEEGCoordinateUnits
fields in*_coordsystem.json. If an ***_electrodes.tsv** file is specified, a ***_coordsystem.json** file MUST be specified as well. The order of the required columns in the
*_electrodes.tsvfile MUST be as listed below.

Column name Requirement Level Data type Description

name REQUIRED string Name of the electrode contact point.
Values innameMUST be unique.This
column must appear first in the file.
x REQUIRED number Recorded position along the x-axis.
This column must appear second in the
file.
y REQUIRED number Recorded position along the y-axis.
This column must appear third in the
file.
z REQUIRED numberor"n/a" Recorded position along the z-axis. This
column must appear fourth in the file.
type RECOMMENDED string Type of the electrode (for example, cup,
ring, clip-on, wire, needle). This column
may appear anywhere in the file.
material RECOMMENDED string Material of the electrode (for example,
Tin,Ag/AgCl,Gold). This column may
appear anywhere in the file.
impedance RECOMMENDED number Impedance of the electrode, units MUST
be inkOhm. This column may appear
anywhere in the file.


Column name Requirement Level Data type Description

Additional Columns OPTIONAL n/a Additional columns are allowed if they
are defined in the associated metadata
file.

#### Example*_electrodes.tsv

See also the correspondingelectrodes.tsvexample.

name x y z type material
VEOG+ n/a n/a n/a cup Ag/AgCl
VEOG- n/a n/a n/a cup Ag/AgCl
FDI+ n/a n/a n/a cup Ag/AgCl
FDI- n/a n/a n/a cup Ag/AgCl
GND -0.0707 0.0000 -0.0707 clip-on Ag/AgCl
Cz 0.0000 0.0714 0.0699 cup Ag/AgCl
REF -0.0742 -0.0200 -0.0100 cup Ag/AgCl

Theacq-<label>entity can be used to indicate acquisition of the same data. For example, this could be the recording of electrode positions with a different electrode
position recording device, or repeated digitization before and after the recording.

### Coordinate System JSON (*_coordsystem.json)

Template:

sub-<label>/
[ses-<label>/]
eeg/
sub-<label>[_ses-<label>][_acq-<label>][_space-<label>]_coordsystem.json

Legend:

- Filename entities or directories between square brackets (for example,[_ses-<label>]) are OPTIONAL.
- Some entities may only allow specific values, in which case those values are listed in<>, separated by|.
- _<suffix>means that there are several (>6) valid suffixes for this filename pattern.
- .<extension>means that there are several (>6) valid extensions for this file type.
- [.gz]means that both the unzipped and gzipped versions of the extension are valid.

A*_coordsystem.jsonfile is used to specify the fiducials, the location of anatomical landmarks, and the coordinate system and units in which the position of electrodes
and landmarks is expressed. The ***_coordsystem.json** is REQUIRED if the optional ***_electrodes.tsv** is specified. If a corresponding anatomical MRI is available, the
locations of landmarks and fiducials according to that scan should also be stored in the*_T1w.jsonfile which goes alongside the MRI data.


For disambiguation, we employ the following definitions for fiducials and anatomical landmarks respectively:

- Fiducialsareobjectswithawelldefinedlocationusedtofacilitatethelocalizationofelectrodesandco-registrationwithothergeometricdatasuchastheparticipant’s
    own T1 weighted magnetic resonance head image, a T1 weighted template head image, or a spherical head model. Commonly used fiducials are vitamin-E pills,
    which show clearly in an MRI, or reflective spheres that are localized with an infrared optical tracking system.
- Anatomical landmarks are locations on a research subject such as the nasion, which is the intersection of the frontal bone and two nasal bones of the human skull.

Fiducials are typically used in conjunction with anatomical landmarks. An example would be the placement of vitamin-E pills on top of anatomical landmarks, or the
placement of LEDs on the nasion and preauricular points to triangulate the position of other LED-lit electrodes on a research subject’s head.

- For more information on the definition of anatomical landmarks, please visit:https://www.fieldtriptoolbox.org/faq/how_are_the_lpa_and_rpa_points_defined
- For more information on coordinate systems for coregistration, please visit:https://www.fieldtriptoolbox.org/faq/how_are_the_different_head_and_mri_coordinat
    e_systems_defined

General fields:

Key name Requirement Level Data type Description

IntendedFor OPTIONAL stringorarray The paths to files for which the
associated file is intended to be used.
Contains one or more IntendedFor.
Using forward-slash separated paths
relative to the participant subdirectory
is IntendedFor. This identifies the MRI
or CT scan associated with the
electrodes, landmarks, and fiducials.

Fields relating to the EEG electrode positions:

Key name Requirement Level Data type Description

EEGCoordinateSystem REQUIRED string Defines the coordinate system for the
EEG sensors.See the
EEGCoordinateSystem for a list of
restricted keywords for coordinate
systems. If"Other", provide definition
of the coordinate system in
EEGCoordinateSystemDescription.
For a list of valid values for this field,
see the EEGCoordinateSystem.


Key name Requirement Level Data type Description

EEGCoordinateUnits REQUIRED string Units of the coordinates of
EEGCoordinateSystem. Must be one of:
"m","mm","cm","n/a".
EEGCoordinateSystemDescription RECOMMENDED, but REQUIRED if
EEGCoordinateSystemis"Other"

```
string Free-form text description of the
coordinate system. May also include a
link to a documentation page or paper
describing the system in greater detail.
```
Fields relating to the position of fiducials measured during an EEG session/run:

Key name Requirement Level Data type Description

FiducialsDescription OPTIONAL string Free-form text description of how the
fiducials such as vitamin-E capsules
were placed relative to anatomical
landmarks, and how the position of the
fiducials were measured (for example,
"both with Polhemus and with T1w
MRI").
FiducialsCoordinates RECOMMENDED objectofarrays Key-value pairs of the labels and 3-D
digitized position of anatomical
landmarks, interpreted following the
"FiducialsCoordinateSystem"(for
example,{"NAS": [12.7,21.3,13.9],
"LPA": [5.2,11.3,9.6], "RPA":
[20.2,11.3,9.1]}). Each array MUST
contain three numeric values
corresponding to x, y, and z axis of the
coordinate system in that exact order.


Key name Requirement Level Data type Description

FiducialsCoordinateSystem RECOMMENDED string Defines the coordinate system for the
fiducials. Preferably the same as the
"EEGCoordinateSystem". See the
FiducialsCoordinateSystem for a list of
restricted keywords for coordinate
systems. If"Other", provide definition
of the coordinate system in
"FiducialsCoordinateSystemDescription".
For a list of valid values for this field,
see the FiducialsCoordinateSystem.
FiducialsCoordinateUnits RECOMMENDED string Units in which the coordinates that are
listed in the field
"FiducialsCoordinateSystem"are
represented. Must be one of:"m","mm",
"cm","n/a".
FiducialsCoordinateSystemDescription RECOMMENDED, but REQUIRED if
FiducialsCoordinateSystemis
"Other"

```
string Free-form text description of the
coordinate system. May also include a
link to a documentation page or paper
describing the system in greater detail.
```
Fields relating to the position of anatomical landmark measured during an EEG session/run:

Key name Requirement Level Data type Description

AnatomicalLandmarkCoordinates RECOMMENDED objectofarrays Key-value pairs of the labels and 3-D
digitized locations of anatomical
landmarks, interpreted following the
"AnatomicalLandmarkCoordinateSystem"
(for example,{"NAS":
[12.7,21.3,13.9], "LPA":
[5.2,11.3,9.6], "RPA":
[20.2,11.3,9.1]}. Each array MUST
contain three numeric values
corresponding to x, y, and z axis of the
coordinate system in that exact order.


Key name Requirement Level Data type Description

AnatomicalLandmarkCoordinateSystem RECOMMENDED string Defines the coordinate system for the
anatomical landmarks. See the Anatom-
icalLandmarkCoordinateSystem for a
list of restricted keywords for
coordinate systems. If"Other", provide
definition of the coordinate system in
"AnatomicalLandmarkCoordinateSystemDescription".
Preferably the same as the
EEGCoordinateSystem.For a list of
valid values for this field, see the
AnatomicalLandmarkCoordinateSys-
tem.
AnatomicalLandmarkCoordinateUnits RECOMMENDED string Units of the coordinates of
"AnatomicalLandmarkCoordinateSystem".
Must be one of:"m","mm","cm","n/a".
AnatomicalLandmarkCoordinateSystemDescriptionRECOMMENDED, but REQUIRED if
AnatomicalLandmarkCoordinateSystem
is"Other"

```
string Free-form text description of the
coordinate system. May also include a
link to a documentation page or paper
describing the system in greater detail.
```
If the position of anatomical landmarks is measured using the same system or device used to measure electrode positions, and if thereby the anatomical landmarks are
expressed in the same coordinates, the coordinates of the anatomical landmarks can be specified inelectrodes.tsv. The same applies to the coordinates of the fiducials.

Anatomical landmarks or fiducials measured on an anatomical MRI that match the landmarks or fiducials during an EEG session/run, must be stored separately in the
corresponding*_T1w.jsonor*_T2w.jsonfile and should be expressed in voxels (starting from[0, 0, 0]).

#### Example*_coordsystem.json

##### {

"IntendedFor":"bids::sub-01/ses-01/anat/sub-01_T1w.nii",
"EEGCoordinateSystem":"Other",
"EEGCoordinateUnits":"mm",
"EEGCoordinateSystemDescription":"RAS orientation: Origin halfway between LPA and RPA, positive x-axis towards RPA, positive y-axis orthogonal to x-axis through Nasion, z-axis orthogonal to xy-plane, pointing in superior direction.",
"FiducialsDescription":"Electrodes and fiducials were digitized with Polhemus, fiducials were recorded as the centre of vitamin E capsules sticked on the left/right pre-auricular and on the nasion, these are also visible on the T1w MRI"
}


### Landmark photos (*_photo.jpg).

Photos of the anatomical landmarks and/or fiducials.

Template:

sub-<label>/
[ses-<label>/]
eeg/
sub-<label>[_ses-<label>][_acq-<label>]_photo.jpg
sub-<label>[_ses-<label>][_acq-<label>]_photo.png
sub-<label>[_ses-<label>][_acq-<label>]_photo.tif

Legend:

- Filename entities or directories between square brackets (for example,[_ses-<label>]) are OPTIONAL.
- Some entities may only allow specific values, in which case those values are listed in<>, separated by|.
- _<suffix>means that there are several (>6) valid suffixes for this filename pattern.
- .<extension>means that there are several (>6) valid extensions for this file type.
- [.gz]means that both the unzipped and gzipped versions of the extension are valid.

Photos of the anatomical landmarks and/or fiducials are OPTIONAL. Please note that the photos may need to be cropped or blurred to conceal identifying features prior
to sharing, depending on the terms of the consent given by the participant.

Theacq-<label>entity can be used to indicate acquisition of different photos of the same face (or other body part in different angles to show, for example, the location
of the nasion (NAS) as opposed to the right periauricular point (RPA).

#### Example*_photo.jpg.

Picture of a NAS fiducial placed between the eyebrows, rather than at the actual anatomical nasion:sub-0001_ses-001_acq-NAS_photo.jpg



## Intracranial Electroencephalography

SupportforIntracranialElectroencephalography(iEEG)wasdevelopedasaBIDSExtensionProposal. PleaseseeCitingBIDSonhowtoappropriatelycreditthisextension
when referring to it in the context of the academic literature.

Severalexample iEEG datasetshave been formatted using this specification and can be used for practical guidance when curating a new dataset.

### iEEG recording data

Template:

sub-<label>/
[ses-<label>/]
ieeg/
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>]_ieeg.<extension>
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>]_ieeg.json
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>]_events.json
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>]_events.tsv
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>][_recording-<label>]_physio.json
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>][_recording-<label>]_physio.tsv.gz
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>][_recording-<label>]_stim.json
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>][_recording-<label>]_stim.tsv.gz

Legend:

- Filename entities or directories between square brackets (for example,[_ses-<label>]) are OPTIONAL.
- Some entities may only allow specific values, in which case those values are listed in<>, separated by|.
- _<suffix>means that there are several (>6) valid suffixes for this filename pattern.
- .<extension>means that there are several (>6) valid extensions for this file type.
- [.gz]means that both the unzipped and gzipped versions of the extension are valid.


The iEEG community uses a variety of formats for storing raw data, and there is no single standard that all researchers agree on. For BIDS, iEEG data MUST be stored
in one of the following formats:

```
Format Extension(s) Description
European data format .edf Each recording consists of a.edfsingle file.edf+files
are permitted. The capital.EDFextension MUST
NOT be used.
BrainVision Core Data Format .vhdr,.vmrk,.eeg Each recording consists of a.vhdr,.vmrk,.eegfile
triplet.
EEGLAB .set,.fdt The format used by the MATLAB toolboxEEGLAB.
Each recording consists of a.setfile with an
OPTIONAL.fdtfile.
Neurodata Without Borders .nwb Each recording consists of a single.nwbfile.
MEF3 .mefd Each recording consists of a.mefddirectory.
```
It is RECOMMENDED to use the European data format, or the BrainVision data format. It is furthermore discouraged to use the other accepted formats over these
RECOMMENDED formats, particularly because there are conversion scripts available in most commonly used programming languages to convert data into the RECOM-
MENDED formats.

Future versions of BIDS may extend this list of supported file formats. File formats for future consideration MUST have open access documentation, MUST have open
source implementation for both reading and writing in at least two programming languages and SHOULD be widely supported in multiple software packages. Other
formats that may be considered in the future should have a clear added advantage over the existing formats and should have wide adoption in the BIDS community.

The data format in which the data was originally stored is especially valuable in case conversion elicits the loss of crucial metadata specific to manufacturers and specific
iEEGsystems. Wealsoencourageuserstoprovideadditionalmetainformationextractedfromthemanufacturer-specificdatafilesinthesidecarJSONfile. Otherrelevant
files MAY be included alongside the original iEEG data in the/sourcedatadirectory.

Note the RecordingType, which depends on whether the data stream on disk is interrupted or not. Continuous data is by definition 1 segment without interruption.
Epoched data consists of multiple segments that all have the same length (for example, corresponding to trials) and that have gaps in between. Discontinuous data
consists of multiple segments of different length, for example due to a pause in the acquisition.

#### Terminology: Electrodes vs. Channels

For proper documentation of iEEG recording metadata it is important to understand the difference between electrode and channel: an iEEG electrode is placed on or in
the brain, whereas a channel is the combination of the analog differential amplifier and analog-to-digital converter that result in a potential (voltage) difference that is
stored in the iEEG dataset. We employ the following short definitions:

- Electrode=Asinglepointofcontactbetweentheacquisitionsystemandtherecordingsite(forexample,scalp,neuraltissue,...). Multipleelectrodescanbeorganized
    as arrays, grids, leads, strips, probes, shafts, caps (for EEG), and so forth.


- Channel=Asingleanalog-to-digitalconverterintherecordingsystemthatregularlysamplesthevalueofatransducer,whichresultsinthesignalbeingrepresented
    asatimeseriesinthedigitizeddata. Thiscanbeconnectedtotwoelectrodes(tomeasurethepotentialdifferencebetweenthem),amagneticfieldormagneticgradient
    sensor, temperature sensor, accelerometer, and so forth.

Although the reference and ground electrodes are often referred to as channels, they are in most common iEEG systems not recorded by themselves. Therefore they are
not represented as channels in the data. The type of referencing for all channels and optionally the location of the reference electrode and the location of the ground
electrode MAY be specified.

#### Sidecar JSON (*_ieeg.json)

For consistency between studies and institutions, we encourage users to extract the values of metadata fields from the actual raw data. Whenever possible, please avoid
using ad hoc wording.

Generic fields MUST be present:

Key name Requirement Level Data type Description

TaskName REQUIRED string Name of the task. No two tasks should
have the same name. The task label
included in the file name is derived from
this"TaskName"field by removing all
non-alphanumeric characters (that is,
all except those matching
[0-9a-zA-Z]). For example
"TaskName" "faces n-back"will
correspond to task labelfacesnback. A
RECOMMENDED convention is to
name resting state task using labels
beginning withrest.

Note that theTaskNamefield does not have to be a ”behavioral task” that subjects perform, but can reflect some information about the conditions present when the data
was acquired (for example,"rest","sleep", or"seizure").

SHOULDbepresent: Forconsistencybetweenstudiesandinstitutions,weencourageuserstoextractthevaluesofthesefieldsfromtheactualrawdata. Wheneverpossible,
please avoid using ad hoc wording.

Key name Requirement Level Data type Description

InstitutionName RECOMMENDED string The name of the institution in charge of
the equipment that produced the
measurements.


Key name Requirement Level Data type Description

InstitutionAddress RECOMMENDED string The address of the institution in charge
of the equipment that produced the
measurements.
InstitutionalDepartmentName RECOMMENDED string The department in the institution in
charge of the equipment that produced
the measurements.
Manufacturer RECOMMENDED string Manufacturer of the equipment that
produced the measurements. For
example,"TDT","Blackrock".
ManufacturersModelName RECOMMENDED string Manufacturer’s model name of the
equipment that produced the
measurements.
SoftwareVersions RECOMMENDED string Manufacturer’s designation of software
version of the equipment that produced
the measurements.
TaskDescription RECOMMENDED string Longer description of the task.
Instructions RECOMMENDED string Text of the instructions given to
participants before the recording. This
is especially important in context of
resting state recordings and
distinguishing between eyes open and
eyes closed paradigms.
CogAtlasID RECOMMENDED string CogAtlasID of the corresponding
Cognitive AtlasTask term.
CogPOID RECOMMENDED string CogPOID of the correspondingCogPO
term.
DeviceSerialNumber RECOMMENDED string The serial number of the equipment
that produced the measurements. A
pseudonym can also be used to prevent
the equipment from being identifiable,
so long as each pseudonym is unique
within the dataset.

Specific iEEG fields MUST be present:


Key name Requirement Level Data type Description

iEEGReference REQUIRED string General description of the reference
scheme used and (when applicable) of
location of the reference electrode in the
raw recordings (for example,"left
mastoid","bipolar","T01"for
electrode with name T01,
"intracranial electrode on top of
a grid, not included with data",
"upside down electrode"). If
different channels have a different
reference, this field should have a
general description and the channel
specific reference should be defined in
thechannels.tsvfile.
SamplingFrequency REQUIRED number Sampling frequency (in Hz) of all the
data in the recording, regardless of their
type (for example, 2400 ). The sampling
frequency of data channels that deviate
from the main sampling frequency
SHOULD be specified in the
channels.tsvfile.
PowerLineFrequency REQUIRED numberor"n/a" Frequency (in Hz) of the power grid at
the geographical location of the
instrument (for example, 50 or 60 ).
SoftwareFilters REQUIRED objectofobjectsor"n/a" Objectof temporal software filters
applied, or"n/a"if the data is not
available. Each key-value pair in the
JSON object is a name of the filter and
an object in which its parameters are
defined as key-value pairs (for example,
{"Anti-aliasing filter":
{"half-amplitude cutoff (Hz)":
500, "Roll-off": "6dB/Octave"}}).

Specific iEEG fields SHOULD be present:


Key name Requirement Level Data type Description

DCOffsetCorrection DCOffsetCorrection string A description of the method (if any)
used to correct for a DC offset. If the
method used was subtracting the mean
value for each channel, use ”mean”.
HardwareFilters RECOMMENDED objectofobjectsor"n/a" Object of temporal hardware filters
applied, or"n/a"if the data is not
available. Each key-value pair in the
JSON object is a name of the filter and
an object in which its parameters are
defined as key-value pairs. For example,
{"Highpass RC filter": {"Half
amplitude cutoff (Hz)": 0.0159,
"Roll-off": "6dB/Octave"}}.
ElectrodeManufacturer RECOMMENDED string Can be used if all electrodes are of the
same manufacturer (for example,
"AD-TECH","DIXI"). If electrodes of
different manufacturers are used,
please use the corresponding table in
the_electrodes.tsvfile.
ElectrodeManufacturersModelName RECOMMENDED string If different electrode types are used,
please use the corresponding table in
the_electrodes.tsvfile.
ECOGChannelCount RECOMMENDED integer Number of ECoG channels. Must be a
number greater than or equal to 0.
SEEGChannelCount RECOMMENDED integer Number of SEEG channels. Must be a
number greater than or equal to 0.
EEGChannelCount RECOMMENDED integer Number of EEG channels recorded
simultaneously (for example, 21 ). Must
be a number greater than or equal to 0.
EOGChannelCount RECOMMENDED integer Number of EOG channels. Must be a
number greater than or equal to 0.
ECGChannelCount RECOMMENDED integer Number of ECG channels. Must be a
number greater than or equal to 0.
EMGChannelCount RECOMMENDED integer Number of EMG channels. Must be a
number greater than or equal to 0.
MiscChannelCount RECOMMENDED integer Number of miscellaneous analog
channels for auxiliary signals. Must be
a number greater than or equal to 0.


Key name Requirement Level Data type Description

TriggerChannelCount RECOMMENDED integer Number of channels for digital (TTL bit
level) triggers. Must be a number
greater than or equal to 0.
RecordingDuration RECOMMENDED number Length of the recording in seconds (for
example, 3600 ).
RecordingType RECOMMENDED string Defines whether the recording is
"continuous","discontinuous", or
"epoched", where"epoched"is limited
to time windows about events of
interest (for example, stimulus
presentations or subject responses).
Must be one of:"continuous",
"epoched","discontinuous".
EpochLength RECOMMENDED number Duration of individual epochs in
seconds (for example, 1 ) in case of
epoched data. If recording was
continuous or discontinuous, leave out
the field. Must be a number greater
than or equal to 0.
iEEGGround RECOMMENDED string Description of the location of the
ground electrode ("placed on right
mastoid (M2)").
iEEGPlacementScheme RECOMMENDED string Freeform description of the placement
of the iEEG electrodes.
Left/right/bilateral/depth/surface (for
example,"left frontal grid and
bilateral hippocampal depth"or
"surface strip and STN depth"or
"clinical indication bitemporal,
bilateral temporal strips and
left grid").
iEEGElectrodeGroups RECOMMENDED string Field to describe the way electrodes are
grouped into strips, grids or depth
probes. For example,"grid1: 10x8
grid on left temporal pole,
strip2: 1x8 electrode strip on
xxx".


Key name Requirement Level Data type Description

SubjectArtefactDescription RECOMMENDED string Freeform description of the observed
subject artefact and its possible cause
(for example,"Vagus Nerve
Stimulator","non-removable
implant"). If this field is set to"n/a", it
will be interpreted as absence of major
source of artifacts except cardiac and
blinks.

Specific iEEG fields MAY be present:

Key name Requirement Level Data type Description

ElectricalStimulation OPTIONAL boolean Boolean field to specify if electrical
stimulation was done during the
recording (options aretrueorfalse).
Parameters for event-like stimulation
should be specified in theevents.tsv
file. Must be one of:"true","false".
ElectricalStimulationParameters OPTIONAL string Free form description of stimulation
parameters, such as frequency or shape.
Specific onsets can be specified in the
events.tsv file. Specific shapes can be
described here in freeform text.

Note that the date and time information SHOULD be stored in the study key file (scans.tsv). Date time information MUST be expressed as indicated in Units

Example ***_ieeg.json**

{
"TaskName":"visual",
"InstitutionName":"Stanford Hospital and Clinics",
"InstitutionAddress":"300 Pasteur Dr, Stanford, CA 94305",
"Manufacturer":"Tucker Davis Technologies",
"ManufacturersModelName":"n/a",
"TaskDescription":"visual gratings and noise patterns",
"Instructions":"look at the dot in the center of the screen and press the button when it changes color",
"iEEGReference":"left mastoid",


"SamplingFrequency": 1000 ,
"PowerLineFrequency": 60 ,
"SoftwareFilters":"n/a",
"HardwareFilters":{"Highpass RC filter": {"Half amplitude cutoff (Hz)":0.0159, "Roll-off": "6dBOctave"}},
"ElectrodeManufacturer":"AdTech",
"ECOGChannelCount": 120 ,
"SEEGChannelCount": 0 ,
"EEGChannelCount": 0 ,
"EOGChannelCount": 0 ,
"ECGChannelCount": 0 ,
"EMGChannelCount": 0 ,
"MiscChannelCount": 0 ,
"TriggerChannelCount": 0 ,
"RecordingDuration":233.639,
"RecordingType":"continuous",
"iEEGGround":"placed on the right mastoid",
"iEEGPlacementScheme":"right occipital temporal surface",
"ElectricalStimulation": **false**
}

### Channels description (*_channels.tsv)

Template:

sub-<label>/
[ses-<label>/]
ieeg/
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>]_channels.json
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>]_channels.tsv

Legend:

- Filename entities or directories between square brackets (for example,[_ses-<label>]) are OPTIONAL.
- Some entities may only allow specific values, in which case those values are listed in<>, separated by|.
- _<suffix>means that there are several (>6) valid suffixes for this filename pattern.
- .<extension>means that there are several (>6) valid extensions for this file type.
- [.gz]means that both the unzipped and gzipped versions of the extension are valid.

A channel represents one time series recorded with the recording system (for example, there can be a bipolar channel, recorded from two electrodes or contact points on
thetissue). AlthoughthisinformationcanoftenbeextractedfromtheiEEGrecording,listingitinasimple.tsvdocumentmakesiteasytobrowseorsearch(forexample,
searchingforrecordingswithasamplingfrequencyof>=1000Hz). Hence, thechannels.tsvfileisRECOMMENDED.ChannelsSHOULDappearinthetableinthesame


order they do in the iEEG data file. Any number of additional columns MAY be provided to provide additional information about the channels. Note that electrode
positions SHOULD NOT be added to this file but to*_electrodes.tsv.

The columns of the channels description table stored in*_channels.tsvare:

Column name Requirement Level Data type Description

name REQUIRED string Label of the channel. When a
corresponding electrode is specified in
_electrodes.tsv, the name of that
electrode MAY be specified here and the
reference electrode name MAY be
provided in thereferencecolumn.
Values innameMUST be unique.This
column must appear first in the file.
type REQUIRED string Type of channel; MUST use the channel
types listed below. Note that the type
MUST be in upper-case. This column
must appear second in the file.For a list
of valid values for this column, see the
type.
units REQUIRED string Physical unit of the value represented
in this channel, for example,Vfor Volt,
orfT/cmfor femto Tesla per centimeter
(see units). This column must appear
third in the file.
low_cutoff REQUIRED numberor"n/a" Frequencies used for the high-pass filter
applied to the channel in Hz. If no
high-pass filter applied, usen/a. This
column may appear anywhere in the
file.
high_cutoff REQUIRED numberor"n/a" Frequencies used for the low-pass filter
applied to the channel in Hz. If no
low-pass filter applied, usen/a. Note
that hardware anti-aliasing in A/D
conversion of all MEG/EEG electronics
applies a low-pass filter; specify its
frequency here if applicable. This
column may appear anywhere in the
file.


Column name Requirement Level Data type Description

reference OPTIONAL stringor"n/a" Specification of the reference (for
example,mastoid,ElectrodeName01,
intracranial,CAR,other,n/a). If the
channel is not an electrode channel (for
example, a microphone channel) use
n/a. This column may appear
anywhere in the file.
group OPTIONAL stringornumber Which group of channels
(grid/strip/seeg/depth) this channel
belongs to. This is relevant because one
group has one cable-bundle and noise
can be shared. This can be a name or
number. Note that any groups specified
in_electrodes.tsvmust match those
present here. This column may appear
anywhere in the file.
sampling_frequency OPTIONAL number Sampling rate of the channel in Hz.
This column may appear anywhere in
the file.
description OPTIONAL string Brief free-text description of the
channel, or other information of
interest. This column may appear
anywhere in the file.
notch OPTIONAL numberor"n/a" Frequencies used for the notch filter
applied to the channel, in Hz. If no
notch filter applied, usen/a. This
column may appear anywhere in the
file.
status OPTIONAL string Data quality observed on the channel.
A channel is consideredbadif its data
quality is compromised by excessive
noise. If quality is unknown, then a
value ofn/amay be used. Description
of noise type SHOULD be provided in
[status_description]. This column
may appear anywhere in the file.Must
be one of:"good","bad","n/a".


Column name Requirement Level Data type Description

status_description OPTIONAL string Freeform text description of noise or
artifact affecting data quality on the
channel. It is meant to explain why the
channel was declared bad in thestatus
column. This column may appear
anywhere in the file.
Additional Columns OPTIONAL n/a Additional columns are allowed if they
are defined in the associated metadata
file.

Restricted keyword list for field type in alphabetic order (shared with the MEG and EEG modality; however, only types that are common in iEEG data are listed here).
Note that upper-case is REQUIRED:

Keyword Description

EEG Electrode channel from electroencephalogram
ECOG Electrode channel from electrocorticogram (intracranial)
SEEG Electrode channel from stereo-electroencephalogram (intracranial)
DBS Electrode channel from deep brain stimulation electrode (intracranial)
VEOG Vertical EOG (electrooculogram)
HEOG Horizontal EOG
EOG Generic EOG channel if HEOG or VEOG information not available
ECG ElectroCardioGram (heart)
EMG ElectroMyoGram (muscle)
TRIG System Triggers
AUDIO Audio signal
PD Photodiode
EYEGAZE Eye Tracker gaze
PUPIL Eye Tracker pupil diameter
MISC Miscellaneous
SYSCLOCK System time showing elapsed time since trial started
ADC Analog to Digital input
DAC Digital to Analog output
REF Reference channel
OTHER Any other type of channel

Examples of free-form text for fielddescription:


- intracranial
- stimulus
- response
- vertical EOG
- skin conductance

#### Example*_channels.tsv.

name type units low_cutoff high_cutoff status status_description
LT01 ECOG uV 300 0.11 good n/a
LT02 ECOG uV 300 0.11 bad broken
H01 SEEG uV 300 0.11 bad line_noise
ECG1 ECG uV n/a 0.11 good n/a
TR1 TRIG n/a n/a n/a good n/a

### Electrode description (*_electrodes.tsv).

Template:

sub-<label>/
[ses-<label>/]
ieeg/
sub-<label>[_ses-<label>][_acq-<label>][_space-<label>]_electrodes.json
sub-<label>[_ses-<label>][_acq-<label>][_space-<label>]_electrodes.tsv

Legend:

- Filename entities or directories between square brackets (for example,[_ses-<label>]) are OPTIONAL.
- Some entities may only allow specific values, in which case those values are listed in<>, separated by|.
- _<suffix>means that there are several (>6) valid suffixes for this filename pattern.
- .<extension>means that there are several (>6) valid extensions for this file type.
- [.gz]means that both the unzipped and gzipped versions of the extension are valid.

Filethatgivesthelocation,sizeandotherpropertiesofiEEGelectrodes. NotethatcoordinatesareexpectedincartesiancoordinatesaccordingtotheiEEGCoordinateSystem
andiEEGCoordinateUnitsfields in*_coordsystem.json. If an*_electrodes.tsvfile is specified, a*_coordsystem.jsonfile MUST be specified as well.

The optionalspace-<label>entity (*[_space-<label>]_electrodes.tsv) can be used to indicate the way in which electrode positions are interpreted. The space
<label>MUST be taken from one of the modality specific lists in the Coordinate Systems Appendix. For example for iEEG data, the restricted keywords listed under
iEEG Specific Coordinate Systems are acceptable for<label>.

For examples:

- *_space-MNI152Lin(electrodes are coregistred and scaled to a specific MNI template)


- *_space-Talairach(electrodes are coregistred and scaled to Talairach space)

When referring to the*_electrodes.tsvfile in a certain space as defined above, thespace-<label>of the accompanying*_coordsystem.jsonMUST correspond.

```
For example:
sub-01/
sub-01_space-Talairach_electrodes.tsv
sub-01_space-Talairach_coordsystem.json
...
The order of the required columns in the*_electrodes.tsvfile MUST be as listed below. Thex,y, andzcolumns indicate the positions of the center of each electrode in
Cartesian coordinates. Units are specified inspace-<label>_coordsystem.json.
```
```
Column name Requirement Level Data type Description
name REQUIRED string Name of the electrode contact point.
Values innameMUST be unique.This
column must appear first in the file.
x REQUIRED number Recorded position along the x-axis.
This column must appear second in the
file.
y REQUIRED number Recorded position along the y-axis.
This column must appear third in the
file.
z REQUIRED numberor"n/a" Recorded position along the z-axis. If
electrodes are in 2D space this should be
a column ofn/avalues. This column
must appear fourth in the file.
size REQUIRED number Surface area of the electrode, units
MUST be inmm^2. This column may
appear anywhere in the file.
material RECOMMENDED string Material of the electrode (for example,
Tin,Ag/AgCl,Gold). This column may
appear anywhere in the file.
manufacturer RECOMMENDED string The manufacturer for each electrode.
Can be used if electrodes were
manufactured by more than one
company. This column may appear
anywhere in the file.
```

Column name Requirement Level Data type Description

group RECOMMENDED stringornumber Which group of channels
(grid/strip/seeg/depth) this channel
belongs to. This is relevant because one
group has one cable-bundle and noise
can be shared. This can be a name or
number. Note that any group specified
here should match a group specified in
_channels.tsv. This column may
appear anywhere in the file.
hemisphere RECOMMENDED string The hemisphere in which the electrode
is placed. This column may appear
anywhere in the file.Must be one of:
"L","R".
type OPTIONAL string Type of the electrode (for example, cup,
ring, clip-on, wire, needle). This column
may appear anywhere in the file.
impedance OPTIONAL number Impedance of the electrode, units MUST
be inkOhm. This column may appear
anywhere in the file.
dimension OPTIONAL string Size of the group (grid/strip/probe) that
this electrode belongs to. Must be of
form[AxB]with the smallest dimension
first (for example,[1x8]). This column
may appear anywhere in the file.
Additional Columns OPTIONAL n/a Additional columns are allowed if they
are defined in the associated metadata
file.

#### Example*_electrodes.tsv

name x y z size manufacturer
LT01 19 -39 -16 2.3 Integra
LT02 23 -40 -19 2.3 Integra
H01 27 -42 -21 5 AdTech

### Coordinate System JSON (*_coordsystem.json)

Template:


sub-<label>/
[ses-<label>/]
ieeg/
sub-<label>[_ses-<label>][_acq-<label>][_space-<label>]_coordsystem.json

Legend:

- Filename entities or directories between square brackets (for example,[_ses-<label>]) are OPTIONAL.
- Some entities may only allow specific values, in which case those values are listed in<>, separated by|.
- _<suffix>means that there are several (>6) valid suffixes for this filename pattern.
- .<extension>means that there are several (>6) valid extensions for this file type.
- [.gz]means that both the unzipped and gzipped versions of the extension are valid.

This*_coordsystem.jsonfile contains the coordinate system in which electrode positions are expressed. The associated MRI, CT, X-Ray, or operative photo can also be
specified.

General fields:

Key name Requirement Level Data type Description

IntendedFor OPTIONAL stringorarray The paths to files for which the
associated file is intended to be used.
Contains one or more IntendedFor.
Using forward-slash separated paths
relative to the dataset root is
IntendedFor. If only a surface
reconstruction is available, this should
point to the surface reconstruction file.
Note that this file should have the same
coordinate system specified in
iEEGCoordinateSystem. For example,
T1:
'bids::sub-<label>/ses-<label>/anat/sub-01_T1w.nii.gz'
Surface:
'bids::derivatives/surfaces/sub-<label>/ses-<label>/anat/
sub-01_hemi-R_desc-T1w_pial.surf.gii'
Operative photo:
'bids::sub-<label>/ses-<label>/ieeg/
sub-0001_ses-01_acq-photo1_photo.jpg'
Talairach:
'bids::derivatives/surfaces/sub-Talairach/ses-01/anat/
sub-Talairach_hemi-R_pial.surf.gii'


Fields relating to the iEEG electrode positions:

Key name Requirement Level Data type Description

iEEGCoordinateSystem REQUIRED string Defines the coordinate system for the
iEEG sensors. See the
iEEGCoordinateSystem for a list of
restricted keywords for coordinate
systems. If"Other", provide definition
of the coordinate system in
iEEGCoordinateSystemDescription.
If positions correspond to pixel indices
in a 2D image (of either a
volume-rendering, surface-rendering,
operative photo, or operative drawing),
this MUST be"Pixels". For more
information, see the section on
iEEGCoordinateSystem. For a list of
valid values for this field, see the
iEEGCoordinateSystem.
iEEGCoordinateUnits REQUIRED string Units of the*_electrodes.tsv. MUST
be"pixels"ifiEEGCoordinateSystem
isPixels. Must be one of:"m","mm",
"cm","pixels","n/a".
iEEGCoordinateSystemDescription RECOMMENDED, but REQUIRED if
iEEGCoordinateSystemis"Other"

string Free-form text description of the
coordinate system. May also include a
link to a documentation page or paper
describing the system in greater detail.
iEEGCoordinateProcessingDescription RECOMMENDED string Has any post-processing (such as
projection) been done on the electrode
positions (for example,
"surface_projection","none").
iEEGCoordinateProcessingReference RECOMMENDED string A reference to a paper that defines in
more detail the method used to localize
the electrodes and to post-process the
electrode positions.

#### Recommended 3D coordinate systems

It is preferred that electrodes are localized in a 3D coordinate system (with respect to a pre- and/or post-operative anatomical MRI or CT scans or in a standard space as
specified in the BIDS Coordinate Systems Appendix about preferred names of coordinate systems, such as ACPC).


#### Allowed 2D coordinate systems

If electrodes are localized in 2D space (only x and y are specified and z is"n/a"), then the positions in this file MUST correspond to the locations expressed in pixels on the
photo/drawing/rendering of the electrodes on the brain. In this case,iEEGCoordinateSystemMUST be defined as"Pixels", andiEEGCoordinateUnitsMUST be defined
as"pixels"(note the difference in capitalization). Furthermore, the coordinates MUST be (row,column) pairs, with (0,0) corresponding to the upper left pixel and (N,0)
corresponding to the lower left pixel.

#### Multiple coordinate systems.

If electrode positions are known in multiple coordinate systems (for example, MRI, CT and MNI), these spaces can be distinguished by the optionalspace-<label>field,
see the*_electrodes.tsv-section for more information. Note that thespace-<label>fields must correspond between*_electrodes.tsvand*_coordsystem.jsonif
they refer to the same data.

#### Example*_coordsystem.json

##### {

"IntendedFor":"bids::sub-01/ses-01/anat/sub-01_T1w.nii.gz",
"iEEGCoordinateSystem":"ACPC",
"iEEGCoordinateUnits":"mm",
"iEEGCoordinateSystemDescription":"Coordinate system with the origin at anterior commissure (AC), negative y-axis going through the posterior commissure (PC), z-axis going to a mid-hemisperic point which lies superior to the AC-PC line, x-axis going to the right",
"iEEGCoordinateProcessingDescription": "surface_projection",
"iEEGCoordinateProcessingReference":"Hermes et al., 2010 JNeuroMeth"
}

### Photos of the electrode positions (*_photo.jpg).

Template:

sub-<label>/
[ses-<label>/]
ieeg/
sub-<label>[_ses-<label>][_acq-<label>]_photo.jpg
sub-<label>[_ses-<label>][_acq-<label>]_photo.png
sub-<label>[_ses-<label>][_acq-<label>]_photo.tif

Legend:

- Filename entities or directories between square brackets (for example,[_ses-<label>]) are OPTIONAL.
- Some entities may only allow specific values, in which case those values are listed in<>, separated by|.
- _<suffix>means that there are several (>6) valid suffixes for this filename pattern.
- .<extension>means that there are several (>6) valid extensions for this file type.
- [.gz]means that both the unzipped and gzipped versions of the extension are valid.


These can include photos of the electrodes on the brain surface, photos of anatomical features or landmarks (such as sulcal structure), and fiducials. Photos can also
include an X-ray picture, a flatbed scan of a schematic drawing made during surgery, or screenshots of a brain rendering with electrode positions. The photos may need
to be cropped and/or blurred to conceal identifying features or entirely omitted prior to sharing, depending on obtained consent.

If there are photos of the electrodes, theacq-<label>entity should be specified with:

- *_photo.jpgin case of an operative photo
- *_acq-xray#_photo.jpgin case of an x-ray picture
- *_acq-drawing#_photo.jpgin case of a drawing or sketch of electrode placements
- *_acq-render#_photo.jpgin case of a rendering

Theses-<label>entity may be used to specify when the photo was taken.

#### Example*_photo.jpg.

ExampleoftheoperativephotoofECoGelectrodes(hereisanannotatedexampleinwhichelectrodesandvasculaturearemarked,takenfromHermesetal.,JNeuroMeth
2010).

```
sub-01/
ses-0001/
sub-0001_ses-01_acq-photo1_photo.jpg
sub-0001_ses-01_acq-photo2_photo.jpg
...
```

Below is an example of a volume rendering of the cortical surface with a superimposed subdural electrode implantation. This map is often provided by the

EEG technician and provided to the epileptologists (for example, see Burneo JG et al.

1. doi:10.1016/j.clineuro.2014.03.020).
    sub-0002_ses-01_acq-render_photo.jpg


### Electrical stimulation

IncaseofelectricalstimulationofbraintissuebypassingcurrentthroughtheiEEGelectrodes,andtheelectricalstimulationhasaneventstructure(on-off,onset,duration),
the*_events.tsvfile can contain the electrical stimulation parameters in addition to other events. Note that these can be intermixed with other task events. Electrical
stimulationparameterscanbedescribedincolumnscalledelectrical_stimulation_<label>,withlabelschosenbytheresearcherandoptionallydefinedinmoredetail
in an accompanying*_events.jsonfile (as per the main BIDS spec). Functions for complex stimulation patterns can, similar as when a video is presented, be stored in a
directory in the/stimuli/directory. For example:/stimuli/electrical_stimulation_functions/biphasic.tsv


#### Example*_events.tsv

onset duration trial_type electrical_stimulation_type electrical_stimulation_site electrical_stimulation_current
1.2 0.001 electrical_stimulation biphasic LT01-LT02 0.005
1.3 0.001 electrical_stimulation biphasic LT01-LT02 0.005
2.2 0.001 electrical_stimulation biphasic LT02-LT03 0.005
4.2 1 electrical_stimulation complex LT02-LT03 n/a
15.2 3 auditory_stimulus n/a n/a n/a


## Task events

```
Thepurposeofthisfileistodescribetimingandotherpropertiesofeventsrecordedduringarun. Eventsare,forexample,stimulipresentedtotheparticipantorparticipant
responses (see Definitions). A single event file MAY include any combination of stimulus, response, and other events. Events MAY overlap in time. Please mind that this
doesnotimplythatonlysocalled”eventrelated”studydesignsaresupported(incontrastto”block”designs)-each”blockofevents”canberepresentedbyanindividual
row in theevents.tsvfile (with a long duration).
Template:
sub-<label>/[ses-<label>]
<data_type>/
<matches>_events.tsv
<matches>_events.json
```
Where<matches>corresponds to task filename. For example:sub-control01_task-nback.

```
Each task events file REQUIRES a corresponding task data file. It is also possible to have a singleevents.tsvfile describing events for all participants and runs (see
Inheritance Principle). As with all other tabular data,events.tsvfiles MAY be accompanied by a JSON file describing the columns in detail (see Tabular Files).
The tabular files consists of one row per event and a set of REQUIRED and OPTIONAL columns:
```

Column name Requirement Level Data type Description

onset REQUIRED number Onset (in seconds) of the event,
measured from the beginning of the
acquisition of the first data point stored
in the corresponding task data file.
Negative onsets are allowed, to account
for events that occur prior to the first
stored data point. For example, in case
there is an in-scanner training phase
that begins before the scanning
sequence has started events from this
sequence should have negative onset
time counting down to the beginning of
the acquisition of the first volume.If
any data points have been discarded
before forming the data file (for
example, ”dummy volumes” in BOLD
fMRI), a time of 0 corresponds to the
first stored data point and not the first
acquired data point. This column must
appear first in the file.
duration REQUIRED numberor"n/a" Duration of the event (measured from
onset) in seconds. Must always be either
zero or positive (orn/aif unavailable).
A ”duration” value of zero implies that
the delta function or event is so short as
to be effectively modeled as an impulse.
This column must appear second in the
file.
sample OPTIONAL integer Onset of the event according to the
sampling scheme of the recorded
modality (that is, referring to the raw
data file that theevents.tsvfile
accompanies). When there are several
sampling schemes present in the raw
data file (as can be the case for example
for.edffiles), this column is ambiguous
and SHOULD NOT be used. This
column may appear anywhere in the
file.


Column name Requirement Level Data type Description

trial_type OPTIONAL string Primary categorisation of each trial to
identify them as instances of the
experimental conditions. For example:
for a response inhibition task, it could
take on valuesgoandno-goto refer to
response initiation and response
inhibition experimental conditions.
This column may appear anywhere in
the file.
response_time OPTIONAL numberor"n/a" Response time measured in seconds. A
negative response time can be used to
represent preemptive responses andn/a
denotes a missed response. This column
may appear anywhere in the file.
value OPTIONAL numberorstring Marker value associated with the event
(for example, the value of a TTL trigger
that was recorded at the onset of the
event). This column may appear
anywhere in the file.
HED OPTIONAL string Hierarchical Event Descriptor (HED)
Tag. See the HED for details. This
column may appear anywhere in the
file.
stim_file OPTIONAL string Represents the location of the stimulus
file (such as an image, video, or audio
file) presented at the given onset time.
There are no restrictions on the file
formats of the stimuli files, but they
should be stored in the/stimuli
directory (under the root directory of
the dataset; with OPTIONAL
subdirectories). The values under the
stim_filecolumn correspond to a path
relative to/stimuli. For example
images/cat03.jpgwill be translated to
/stimuli/images/cat03.jpg. This
column may appear anywhere in the
file.


Column name Requirement Level Data type Description

Additional Columns OPTIONAL n/a Additional columns are allowed.

Note for MRI data: If any acquired scans have been discarded before forming the imaging data file, ensure that anonsetof 0 corresponds to the time the first image was
stored. For example in case there is an in scanner training phase that begins before the scanning sequence has started events from this sequence should have negative
onset time counting down to the beginning of the acquisition of the first volume.

Note regarding the precision of numeric metadata: It is RECOMMENDENDED that dataset curators specify numeric metadata likeonsetanddurationwith as much
decimal precision as is reasonable in the context of the experiment. For example in an EEG experiment with devices operating at 1000 Hz sampling frequency, dataset
curators SHOULD specify at least 3 figures after the decimal point.

An arbitrary number of additional columns can be added. Those allow describing other properties of events that could be later referenced in modelling and hypothesis
extensions of BIDS. Note that thetrial_typeand any additional columns in a TSV file SHOULD be documented in an accompanying JSON sidecar file.

Example:

```
sub-control01/
func/
sub-control01_task-stopsignal_events.tsv
sub-control01_task-stopsignal_events.json
```
Example of the content of the TSV file:

onset duration trial_type response_time stim_file
1.23 0.65 start 1.435 images/red_square.jpg
5.65 0.65 stop 1.739 images/blue_square.jpg

In the accompanying JSON sidecar, thetrial_typecolumn might look as follows:

{
"trial_type":{
"LongName": "Event category",
"Description":"Indicator of type of action that is expected",
"Levels":{
"start": "A red square is displayed to indicate starting",
"stop": "A blue square is displayed to indicate stopping"
}
}
}

Note that all other columns SHOULD also be described but are omitted for the sake of brevity.

For multi-echo files, theevents.tsvfile is applicable to all echos of a particular run:


```
sub-01/
func/
sub-01_task-cuedSGT_run-1_events.tsv
sub-01_task-cuedSGT_run-1_echo-1_bold.nii.gz
sub-01_task-cuedSGT_run-1_echo-2_bold.nii.gz
sub-01_task-cuedSGT_run-1_echo-3_bold.nii.gz
```
Note: Events can also be documented in machine-actionable form using HED (Hierarchical Event Descriptor) tags. This type of documentation is particularly useful for
datasets likely to be used in event-related analyses. See Hierarchical Event Descriptors for additional information and examples.

### Stimuli

Additional information about the stimuli can be added in theevents.tsvandevents.jsonfiles.

This can be done by using a/stimulidirectory or by reference to a stimuli database.

#### Stimuli directory

Thestimulusfilescanbeaddedina/stimulidirectory(undertherootdirectoryofthedataset;withoptionalsubdirectories)ANDusingastim_filecolumninevents.tsv
mentioning which stimulus file was used for a given event,

There are no restrictions on the file formats of the stimuli files, but they should be stored in the/stimulidirectory.

#### Stimuli databases.

References to existing databases can also be encoded using additional columns. The following example includes references to theKarolinska Directed Emotional Faces
(KDEF) database.

Example:

```
sub-control01/
func/
sub-control01_task-emoface_events.tsv
sub-control01_task-emoface_events.json
```
Example of the content of the TSV file:

onset duration trial_type identifier database response_time
1.2 0.6 afraid AF01AFAF kdef 1.435
5.6 0.6 angry AM01AFAN kdef 1.739
5.6 0.6 sad AF01ANSA kdef 1.739

Thetrial_typeandidentifiercolumns from theevents.tsvfiles might be described in the accompanying JSON sidecar as follows:


##### {

"trial_type":{
"LongName": "Emotion image type",
"Description":"Type of emotional face from Karolinska database that is displayed",
"Levels":{
"afraid":"A face showing fear is displayed",
"angry": "A face showing anger is displayed",
"sad":"A face showing sadness is displayed"
}
},
"identifier":{
"LongName": "Karolinska (KDEF) database identifier",
"Description":"ID from KDEF database used to identify the displayed image"
}
}

Note that all other columns SHOULD also be described but are omitted for the sake of brevity.

#### Stimulus presentation details

It is RECOMMENDED to include details of the stimulus presentation software, when applicable:

Key name Requirement Level Data type Description

StimulusPresentation RECOMMENDED object Object containing key-value pairs
related to the software used to present
the stimuli during the experiment,
specifically:"OperatingSystem",
"SoftwareName","SoftwareRRID",
"SoftwareVersion"and"Code". See
table below for more information.

The object supplied forStimulusPresentationSHOULD include the following key-value pairs:

Key name Requirement Level Data type Description

OperatingSystem RECOMMENDED string Operating system used to run the
stimuli presentation software (for
formatting recommendations, see
examples below this table).


Key name Requirement Level Data type Description

SoftwareName RECOMMENDED string Name of the software that was used to
present the stimuli.
SoftwareRRID RECOMMENDED string Research Resource Identifierof the
software that was used to present the
stimuli. Examples: The RRID for
Psychtoolbox is ’SCR_002881’, and that
of PsychoPy is ’SCR_006571’.
SoftwareVersion RECOMMENDED string Version of the software that was used
to present the stimuli.
Code RECOMMENDED string Code of the code used to present the
stimuli. Persistent identifiers such as
DOIs are preferred. If multiple versions
of code may be hosted at the same
location, revision-specific URIs are
RECOMMENDED.

The operating system description SHOULD include the following attributes:

- type (for example, Windows, macOS, Linux)
- distribution (if applicable, for example, Ubuntu, Debian, CentOS)
- the version number (for example, 18.04.5)

Examples:

- Windows 10, Version 2004
- macOS 10.15.6
- Linux Ubuntu 18.04.5

The amount of information supplied for theOperatingSystemSHOULD be sufficient to re-run the code under maximally similar conditions.

The information related to stimulus presentation might be described in the accompanying JSON sidecar as follows (based on the example of the previous section):

{
"trial_type":{
"LongName": "Emotion image type",
"Description":"Type of emotional face from Karolinska database that is displayed",
"Levels":{
"afraid":"A face showing fear is displayed",
"angry": "A face showing anger is displayed",
"sad": "A face showing sadness is displayed"
}


##### },

"identifier":{
"LongName": "Unique identifier from Karolinska (KDEF) database",
"Description":"ID from KDEF database used to identify the displayed image"
},
"StimulusPresentation":{
"OperatingSystem":"Linux Ubuntu 18.04.5",
"SoftwareName": "Psychtoolbox",
"SoftwareRRID": "SCR_002881",
"SoftwareVersion":"3.0.14",
"Code": "doi:10.5281/zenodo.3361717"
}
}


## Physiological and other continuous recordings

Physiologicalrecordingssuchascardiacandrespiratorysignalsandothercontinuousmeasures(suchasparametersofafilmoraudiostimuli)MAYbespecifiedusingtwo
files:

1. agzipcompressed TSV file with data (without header line)
2. a JSON file for storing metadata fields (see below)

Example datasetswith physiological data have been formatted using this specification and can be used for practical guidance when curating a new dataset:

- 7t_trt
- ds210

Template:

sub-<label>/[ses-<label>/]
<datatype>/
<matches>[_recording-<label>]_physio.tsv.gz
<matches>[_recording-<label>]_physio.json
<matches>[_recording-<label>]_stim.tsv.gz
<matches>[_recording-<label>]_stim.json

For the template directory name,<datatype>can correspond to any data recording modality, for examplefunc,anat,dwi,meg,eeg,ieeg, orbeh.

In the template filenames, the<matches>part corresponds to task filename before the suffix. For example for the filesub-control01_task-nback_run-1_bold.nii.gz,
<matches>would correspond tosub-control01_task-nback_run-1.

Note that when supplying a*_<physio|stim>.tsv.gzfile, an accompanying*_<physio|stim>.jsonMUST be supplied as well.

Therecording-<label>entity MAY be used to distinguish between several recording files. For examplesub-01_task-bart_recording-eyetracking_physio.tsv.gz
tocontaintheeyetrackingdatainacertainsamplingfrequency,andsub-01_task-bart_recording-breathing_physio.tsv.gztocontainrespiratorymeasurementsin
a different sampling frequency.

Physiological recordings (including eyetracking) SHOULD use the_physiosuffix, and signals related to the stimulus SHOULD use_stimsuffix.


The following table specifies metadata fields for the*_<physio|stim>.jsonfile.

Key name Requirement Level Data type Description

SamplingFrequency REQUIRED number Sampling frequency (in Hz) of all the
data in the recording, regardless of their
type (for example, 2400 ).
StartTime REQUIRED number Start time in seconds in relation to the
start of acquisition of the first data
sample in the corresponding neural
dataset (negative values are allowed).
Columns REQUIRED arrayofstrings Names of columns in file.
Manufacturer RECOMMENDED string Manufacturer of the equipment that
produced the measurements.
ManufacturersModelName RECOMMENDED string Manufacturer’s model name of the
equipment that produced the
measurements.
SoftwareVersions RECOMMENDED string Manufacturer’s designation of software
version of the equipment that produced
the measurements.
DeviceSerialNumber RECOMMENDED string The serial number of the equipment
that produced the measurements. A
pseudonym can also be used to prevent
the equipment from being identifiable,
so long as each pseudonym is unique
within the dataset.

Additional metadata may be included as in any TSV file to specify, for example, the units of the recorded time series. Please note that, in contrast to other TSV files in
BIDS,theTSVfilesspecifiedforphysiologicalandothercontinuousrecordingsdonotincludeaheaderline. InsteadthenameofcolumnsarespecifiedintheJSONfile(see
Columnsfield). This is to improve compatibility with existing software (for example, FSL, PNM) as well as to make support for other file formats possible in the future.
As in any TSV file, column names MUST NOT be blank (that is, an empty string), and MUST NOT be duplicated within a single JSON file describing a headerless TSV file.

Example*_physio.tsv.gz:

```
sub-control01/
func/
sub-control01_task-nback_physio.tsv.gz
```
(after decompression)

34 110 0
44 112 0


##### 23 100 1

Example*_physio.json:

```
sub-control01/
func/
sub-control01_task-nback_physio.json
```
{
"SamplingFrequency": 100.0,
"StartTime": -22.345,
"Columns":["cardiac","respiratory"],
"Manufacturer": "Brain Research Equipment ltd.",
"cardiac":{
"Description":"continuous pulse measurement",
"Units": "mV"
},
"respiratory":{
"Description":"continuous measurements by respiration belt",
"Units": "mV"
}
}

Note how apart from the general metadata fields likeSamplingFrequency,StartTime,Columns, andManufacturer, each individual column in the TSV file may be
documentedasitsownfieldintheJSONfile(identicaltothepracticeinotherTSV+JSONfilepairs). Here, onlytheDescriptionandUnitsfieldsareshown, butyoumay
use any other of the defined fields such asTermURL,LongName, and so on. In this example, the"cardiac"and"respiratory"time series are produced by devices from
the same manufacturer and follow the same sampling frequency. To specify different sampling frequencies or manufacturers, the time series would have to be split into
separate files like*_recording-cardiac_physio.<tsv.gz|json>and*_recording-respiratory_physio.<tsv.gz|json>.

### Recommendations for specific use cases

To store pulse or breathing measurements, or the scanner trigger signal, the following naming conventions SHOULD be used for the column names:

Column name Requirement Level Data type Description

cardiac OPTIONAL number continuous pulse measurement
respiratory OPTIONAL number continuous breathing measurement
trigger OPTIONAL number continuous measurement of the scanner
trigger signal
Additional Columns OPTIONAL n/a Additional columns are allowed.

For any other data to be specified in columns, the column names can be chosen as deemed appropriate by the researcher.


Recordings with different sampling frequencies or starting times should be stored in separate files (and therecording-<label>entity MAY be used to distinguish these
files).

If the same continuous recording has been used for all subjects (for example in the case where they all watched the same movie), one file MAY be used and placed in the
root directory. For example,task-movie_stim.tsv.gz

For motion parameters acquired from MRI scanner side motion correction, the_physiosuffix SHOULD be used.

For multi-echo data, a givenphysio.tsvfile is applicable to all echos of a particular run. For example:

```
sub-01/
func/
sub-01_task-cuedSGT_run-1_physio.tsv.gz
sub-01_task-cuedSGT_run-1_echo-1_bold.nii.gz
sub-01_task-cuedSGT_run-1_echo-2_bold.nii.gz
sub-01_task-cuedSGT_run-1_echo-3_bold.nii.gz
```

## Behavioral experiments (with no neural recordings)

Template:

sub-<label>/
[ses-<label>/]
beh/
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>]_beh.json
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>]_beh.tsv
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>]_events.json
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>]_events.tsv
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>][_recording-<label>]_physio.json
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>][_recording-<label>]_physio.tsv.gz
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>][_recording-<label>]_stim.json
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>][_recording-<label>]_stim.tsv.gz

Legend:

- Filename entities or directories between square brackets (for example,[_ses-<label>]) are OPTIONAL.
- Some entities may only allow specific values, in which case those values are listed in<>, separated by|.
- _<suffix>means that there are several (>6) valid suffixes for this filename pattern.
- .<extension>means that there are several (>6) valid extensions for this file type.
- [.gz]means that both the unzipped and gzipped versions of the extension are valid.

In addition to logs from behavioral experiments performed alongside imaging data acquisitions, one can also include data from experiments performed with no neural
recordings. The results of those experiments can be stored in thebehdirectory using the same formats for event timing (_events.tsv), metadata (_events.json),
physiological(_physio.tsv.gz,_physio.json)andothercontinuousrecordings(_stim.tsv.gz,_stim.json)asfortasksperformedduringMRI,electrophysiologicalor
other neural recordings. Additionally, events files that do not include the mandatoryonsetanddurationcolumns can still be included, but should be labeled_beh.tsv
rather than_events.tsv.

EachtaskhasauniquelabelthatMUSTonlyconsistoflettersand/ornumbers(othercharacters,includingspacesandunderscores,arenotallowed)withthetask-<label>
entity. Those labels MUST be consistent across subjects and sessions.


The OPTIONALacq-<label>entity corresponds to a custom label to distinguish different conditions present during multiple runs of the same task. For example, if
a study includes runs of an n-back task, with deep brain stimulation turned on or off, the data files may be labelledsub-01_task-nback_acq-dbson_beh.tsvand
sub-01_task-nback_acq-dbsoff_beh.tsv.

### RECOMMENDED metadata

In addition to the metadata that is either:

- RECOMMENDED for sidecar JSON files for tabular data, or
- REQUIRED for some data that can be found in thebehdirectory (for exampleSamplingFrequencyandStartTimefor*_<physio|stim>.tsv.gzfiles),

it is RECOMMENDED to add the following metadata to the JSON files of this directory:

Key name Requirement Level Data type Description

TaskName RECOMMENDED string Name of the task. No two tasks should
have the same name. The task label
included in the file name is derived from
this"TaskName"field by removing all
non-alphanumeric characters (that is,
all except those matching
[0-9a-zA-Z]). For example
"TaskName" "faces n-back"will
correspond to task labelfacesnback.
Instructions RECOMMENDED string Text of the instructions given to
participants before the recording.
TaskDescription RECOMMENDED string Longer description of the task.
CogAtlasID RECOMMENDED string CogAtlasID of the corresponding
Cognitive AtlasTask term.
CogPOID RECOMMENDED string CogPOID of the correspondingCogPO
term.
InstitutionName RECOMMENDED string The name of the institution in charge of
the equipment that produced the
measurements.
InstitutionAddress RECOMMENDED string The address of the institution in charge
of the equipment that produced the
measurements.
InstitutionalDepartmentName RECOMMENDED string The department in the institution in
charge of the equipment that produced
the measurements.


Example of the content of a_beh.tsvand its accompanying_beh.jsonsidecar file:

trial response response_time stim_file
congruent red 1.435 images/word-red_color-red.jpg
incongruent red 1.739 images/word-red_color-blue.jpg

In the accompanying JSON sidecar, thetrialcolumn might be documented as follows:

{
"TaskName":"Stroop",
"trial": {
"LongName":"Trial name",
"Description": "Indicator of the type of trial",
"Levels": {
"congruent":"Word and font color match.",
"incongruent": "Word and font color do not match."
}
}
}


## Genetic Descriptor

Support genetic descriptors was developed as a BIDS Extension Proposal. Please see Citing BIDS on how to appropriately credit this extension when referring to it in the
context of the academic literature.

Geneticdata are typically storedin dedicated repositories, separate from imagingdata. A genetic descriptor links aBIDS dataset to associatedgenetic data, potentially in
a separate repository, with details of where to find the genetic data and the type of data available.

The following example dataset with genetics data have been formatted using this specification and can be used for practical guidance when curating a new dataset.

- UK biobank

### Dataset Description

Genetic descriptors are encoded as an additional, OPTIONAL entry in thedataset_description.jsonfile.

Datasets linked to a genetic database entry include the following REQUIRED or OPTIONALdataset_description.jsonkeys (a dot in the key name denotes a key in a
sub-object, see the example further below):

Key name Requirement Level Data type Description

Dataset REQUIRED string Dataset where data can be retrieved.
Database OPTIONAL string Database of database where the dataset
is hosted.
Descriptors OPTIONAL stringorarrayofstrings List of relevant descriptors (for
example, journal articles) for dataset
using a valid Descriptors when possible.

Example:

{
"Name":"Human Connectome Project",


"BIDSVersion": "1.3.0",
"License":"CC0",
"Authors":["1st author","2nd author"],
"Funding":["P41 EB015894/EB/NIBIB NIH HHS/United States"],
"Genetics":{
"Dataset": "https://www.ncbi.nlm.nih.gov/projects/gap/cgi-bin/study.cgi?study_id=phs001364.v1.p1",
"Database": "https://www.ncbi.nlm.nih.gov/gap/",
"Descriptors": ["doi:10.1016/j.neuroimage.2013.05.041"]
}
}

### Subject naming and Participants file

Ifthesameparticipantshavedifferentidentifiersinthegeneticandimagingdatasets,thecolumngenetic_idSHOULDbeaddedtotheparticipants.tsvfiletoassociate
the BIDS participant with a subject in theGenetics.Datasetreferred to in thedataset_description.jsonfile.

Information about the presence/absence of specific genetic markers MAY be duplicated in theparticipants.tsvfile by adding optional columns (likeidh_mutationin
the example below). Note that optional columns MUST be further described in an accompanyingparticipants.jsonfile as described in Tabular files.

participants.tsvexample:

participant_id age sex group genetic_id idh_mutation
sub-control01 34 M control 124587 yes
sub-control02 12 F control 548936 yes
sub-patient01 33 F patient 489634 no

### Genetic Information

Template:

genetic_info.json

Thegenetic_info.jsonfiledescribesthegeneticinformationavailableintheparticipants.tsvfileand/orthegeneticdatabasedescribedindataset_description.json.
Datasets containing theGeneticsfield indataset_description.jsonor thegenetic_idcolumn inparticipants.tsvMUST include this file with the following fields:

Key name Requirement Level Data type Description

GeneticLevel REQUIRED stringorarrayofstrings Describes the level of analysis. Values
MUST be one of"Genetic","Genomic",
"Epigenomic","Transcriptomic",
"Metabolomic", or"Proteomic".


Key name Requirement Level Data type Description

AnalyticalApproach OPTIONAL stringorarrayofstrings Methodology or methodologies used to
analyse the"GeneticLevel". Values
MUST be taken from thedatabase of
Genotypes and Phenotypes (dbGaP)
under /Study/Molecular Data Type (for
example, SNP Genotypes (Array) or
Methylation (CpG).
SampleOrigin REQUIRED string Describes from which tissue the genetic
information was extracted. Must be one
of:"blood","saliva","brain","csf",
"breast milk","bile","amniotic
fluid","other biospecimen".
TissueOrigin OPTIONAL string Describes the type of tissue analyzed for
"SampleOrigin" brain. Must be one of:
"gray matter","white matter",
"csf","meninges","macrovascular",
"microvascular".
BrainLocation OPTIONAL string Refers to the location in space of the
"TissueOrigin". Values may be an
MNI coordinate, a label taken from the
Allen Brain Atlas, or layer to refer to
layer-specific gene expression, which
can also tie up with laminar fMRI.
CellType OPTIONAL string Describes the type of cell analyzed.
Values SHOULD come from thecell
ontology.

To ensure dataset description consistency, we recommend followingMulti-omics approaches to diseaseby Hasin et al. 2017 to determine theGeneticLevel:

- Genetic: data report on a single genetic location (typically directly in theparticipants.tsvfile)
- Genomic: data link to participants’ genome (multiple genetic locations)
- Epigenomic: data link to participants’ characterization of reversible modifications of DNA
- Transcriptomic: data link to participants RNA levels
- Metabolomic: data link to participants’ products of cellular metabolic functions
- Proteomic: data link to participants peptides and proteins quantification

genetic_info.jsonexample:

{
"GeneticLevel":"Genomic",


"AnalyticalApproach": ["Whole Genome Sequencing","SNP/CNV Genotypes"],
"SampleOrigin":"brain",
"TissueOrigin":"gray matter",
"CellType": "neuron",
"BrainLocation":"[-30 -15 10]"
}


## Positron Emission Tomography

Support for Positron Emission Tomography (PET) was developed as a BIDS Extension Proposal. Please see Citing BIDS on how to appropriately credit this extension
when referring to it in the context of the academic literature.

Severalexample PET datasetshave been formatted using this specification and can be used for practical guidance when curating a new dataset.

Further PET datasets are available fromOpenNeuro.

### Terminology and conventions.

PET-BIDSisfullyconsistentwiththeBIDSspecificationasawhole. However,BIDSwasinitiallydevelopedinthecontextofMRI,sosometerminologymaybeunfamiliar
to researchers from each field. This section adds clarifications to Common Principles - Definitions for the PET context, and introduces the term ”time zero” which is
currently specific to PET.

1. Session - In most cases, a new session with respect to PET corresponds to a visit to the scanning site, and starts with a new injection. In situations where different
    data types are obtained over several visits (for example, FDG PET on one day followed by amyloid PET a couple days after) these scans may be grouped into the
    same session. In other datasets, a subject leaving the scanner and returning under the same injection may be considered separate sessions.
2. Run - In PET, subjects may have to leave the scanner to use the bathroom. While leaving the scanner would interrupt an MR acquisition, in PET this disruption is
    more appropriately considered missing data during a run.
3. Time zero - A reference point in time, to which all timestamps pertaining to a recording are relative. Time zero will most commonly be the time of injection of a
    radioisotope, or the time at which the first scan of an acquisition is begun. If a pharmacological within-scan challenge is performed, another time zero may be more
    convenient.

An overview of a common PET experiment (with blood data) can be seen in Figure 1, defined on a single time scale relative to a predefined ”time zero”.



Figure 1: Overview of a common PET experiment, including blood measurements, and defined on a common time scale. Note, ”time zero” is often defined as time of
injection or scan start, but if a pharmaceutical challenge is carried out during the scan, this time point may also be chosen as time zero. The injected dose, the PET data,
and blood data should all be decay-corrected to time zero, but because the time of injection does not always coincide with scan start, the PET data may not always be
decay-correctedtothetimeofinjection. Ifthisisnotthecase,thismaybeindicatedinthereconstructionsection(ImageDecayCorrectedandImageDecayCorrectionTime).
In this example, tracer injection coincides with scan start.

### PET recording data

Template:

sub-<label>/
[ses-<label>/]
pet/
sub-<label>[_ses-<label>][_task-<label>][_trc-<label>][_rec-<label>][_run-<index>]_pet.json
sub-<label>[_ses-<label>][_task-<label>][_trc-<label>][_rec-<label>][_run-<index>]_pet.nii[.gz]
sub-<label>[_ses-<label>]_task-<label>[_trc-<label>][_rec-<label>][_run-<index>]_events.json
sub-<label>[_ses-<label>]_task-<label>[_trc-<label>][_rec-<label>][_run-<index>]_events.tsv
sub-<label>[_ses-<label>]_task-<label>[_trc-<label>][_rec-<label>][_run-<index>][_recording-<label>]_physio.json
sub-<label>[_ses-<label>]_task-<label>[_trc-<label>][_rec-<label>][_run-<index>][_recording-<label>]_physio.tsv.gz
sub-<label>[_ses-<label>]_task-<label>[_trc-<label>][_rec-<label>][_run-<index>][_recording-<label>]_stim.json
sub-<label>[_ses-<label>]_task-<label>[_trc-<label>][_rec-<label>][_run-<index>][_recording-<label>]_stim.tsv.gz

Legend:

- Filename entities or directories between square brackets (for example,[_ses-<label>]) are OPTIONAL.
- Some entities may only allow specific values, in which case those values are listed in<>, separated by|.
- _<suffix>means that there are several (>6) valid suffixes for this filename pattern.
- .<extension>means that there are several (>6) valid extensions for this file type.
- [.gz]means that both the unzipped and gzipped versions of the extension are valid.

PET data MUST be stored in thepetdirectory. PET imaging data SHOULD be stored in 4D (or 3D, if only one volume was acquired) NIfTI files with the_petsuffix.
Volumes MUST be stored in chronological order (the order they were acquired in).

The OPTIONALtask-<label>is used to indicate a task subjects were asked to perform in the scanner. Those labels MUST be consistent across subjects and sessions. For
task based PET, a correspondingtask eventsfile MUST be provided (please note that this file is not necessary for resting scans).

Thetrc-<label>entityisusedtoindicatethetracerused. ThisentityisOPTIONALifonlyonetracerisusedinthestudy,butREQUIREDtodistinguishbetweentracers
if multiple are used. The label used is arbitrary and each file requires a separate JSON sidecar with details of the tracer used (see below). Examples aretrc-18FFDGfor
fludeoxyglucose ortrc-11CPIBfor Pittsburgh compound B. Other labels are permitted, as long as they are consistent across subjects and sessions and consist only of the
legal label characters.

If more than one run of the same task and acquisition (tracer) are acquired during the same session, therun-<index>entity MUST be used:_run-1,_run-2,_run-3, and
so on. If only one run was acquired therun-<index>can be omitted.


The OPTIONALrec-<label>entity is used to indicate the reconstruction method used for the image, with four reserved values:

- acdyn, for reconstructions with attenuation correction of dynamic data;
- acstat, for reconstructions with attenuation correction of static data;
- nacdyn, for reconstructions without attenuation correction of dynamic data;
- nacstat, for reconstructions without attenuation correction of static data.

Further details regarding reconstruction are in the_pet.jsonfile. If multiple reconstructions of the data are made with the same type of reconstruction, a number MAY
be appended to the label, for examplerec-acdyn1andrec-acdyn2.

#### Shared MRI data along with PET.

PET and MRI images may be aggregated in the same dataset. When analyzing MRI and PET data together, it is essential to specify whether MR images have been
correctedforgradientnon-linearities, usingtheNonLinearGradientCorrectionmetadatafield(seeSequenceSpecifics), whichisREQUIREDforallMRdataifPETdata
is also present in the dataset (see also PET-MRI correspondence). In the case of studies using combined PET/fMRI, subject-specific tasks may be carried out during the
acquisition within the same session. If the same task is recorded with both modalities, the sametask-<label>entity SHOULD be used. For further details, see Task
(including resting state) imaging data.

In addition to the imaging data (*.nii) a_pet.jsonsidecar file MUST be provided. The included metadata are divided into sections described below.

#### PET metadata

PET data MUST be described by metadata fields, stored in sidecar JSON files. These fields are derived from the recommendations in Knudsen et al. 2020,
doi:10.1177/0271678X20905433, which we divide into several categories:

Scanner Hardware

Key name Requirement Level Data type Description

Manufacturer REQUIRED string Manufacturer of the equipment that
produced the measurements.
Corresponds to DICOM Tag 0008, 0070
Manufacturer.
ManufacturersModelName REQUIRED string Manufacturer’s model name of the
equipment that produced the
measurements. Corresponds to DICOM
Tag 0008, 1090Manufacturers Model
Name.


Key name Requirement Level Data type Description

Units REQUIRED string Measurement units for the associated
file. SI units in CMIXF formatting are
RECOMMENDED (see Units). SI unit
for radioactivity (Becquerel) should be
used (for example, ”Bq/mL”).
Corresponds to DICOM Tag 0054, 1001
Units.
InstitutionName RECOMMENDED string The name of the institution in charge of
the equipment that produced the
measurements. Corresponds to DICOM
Tag 0008, 0080InstitutionName.
InstitutionAddress RECOMMENDED string The address of the institution in charge
of the equipment that produced the
measurements. Corresponds to DICOM
Tag 0008, 0081InstitutionAddress.
InstitutionalDepartmentName RECOMMENDED string The department in the institution in
charge of the equipment that produced
the measurements. Corresponds to
DICOM Tag 0008, 1040Institutional
Department Name.
BodyPart RECOMMENDED string Body part of the organ / body region
scanned. Corresponds to DICOM Tag
0018, 0015Body Part Examined.

Radiochemistry

Key name Requirement Level Data type Description

TracerName REQUIRED string Name of the tracer compound used (for
example,"CIMBI-36") Corresponds to
DICOM Tags (0008,0105)Mapping
Resourceand (0008,0122)Mapping
Resource Name.
TracerRadionuclide REQUIRED string Radioisotope labelling tracer (for
example,"C11"). Corresponds to
DICOM Tags (0008,0104)CodeValue
and (0008,0104)CodeMeaning.


Key name Requirement Level Data type Description

InjectedRadioactivity REQUIRED number Total amount of radioactivity injected
into the patient (for example, 400 ). For
bolus-infusion experiments, this value
should be the sum of all injected
radioactivity originating from both
bolus and infusion. Corresponds to
DICOM Tag 0018, 1074Radionuclide
Total Dose.
InjectedRadioactivityUnits REQUIRED string Unit format of the specified injected
radioactivity (for example,"MBq").
InjectedMass REQUIRED numberor"n/a" Total mass of radiolabeled compound
injected into subject (for example, 10 ).
This can be derived as the ratio of the
"InjectedRadioactivity"and
"MolarRadioactivity". For those
tracers in which injected mass is not
available (for example FDG) can be set
to **"n/a"** ).
InjectedMassUnits REQUIRED stringor"n/a" Unit format of the mass of compound
injected (for example,"ug"or"umol").
Note this is not REQUIRED for an FDG
acquisition, since it is not available, and
SHOULD be set to **"n/a"**.
SpecificRadioactivity REQUIRED numberor"n/a" Specific activity of compound injected.
Note this is not REQUIRED for an FDG
acquisition, since it is not available, and
SHOULD be set to **"n/a"**.
SpecificRadioactivityUnits REQUIRED stringor"n/a" Unit format of specified specific
radioactivity (for example,"Bq/g").
Note this is not REQUIRED for an FDG
acquisition, since it is not available, and
SHOULD be set to **"n/a"**.
ModeOfAdministration REQUIRED string Mode of administration of the injection
(for example,"bolus","infusion", or
"bolus-infusion").
TracerRadLex RECOMMENDED string ID of the tracer compound from the
RadLex Ontology.


Key name Requirement Level Data type Description

TracerSNOMED RECOMMENDED string ID of the tracer compound from the
SNOMED Ontology (subclass of
Radioactive isotope).
TracerMolecularWeight RECOMMENDED number Accurate molecular weight of the tracer
used.
TracerMolecularWeightUnits RECOMMENDED string Unit of the molecular weights
measurement (for example,"g/mol").
InjectedMassPerWeight RECOMMENDED number Injected mass per kilogram bodyweight.
InjectedMassPerWeightUnits RECOMMENDED string Unit format of the injected mass per
kilogram bodyweight (for example,
"ug/kg").
SpecificRadioactivityMeasTime RECOMMENDED string Time to which specific radioactivity
measurement above applies in the
default unit"hh:mm:ss".
MolarActivity RECOMMENDED number Molar activity of compound injected.
Corresponds to DICOM Tag 0018, 1077
Radiopharmaceutical Specific
Activity.
MolarActivityUnits RECOMMENDED string Unit of the specified molar radioactivity
(for example,"GBq/umol").
MolarActivityMeasTime RECOMMENDED string Time to which molar radioactivity
measurement above applies in the
default unit"hh:mm:ss".
InfusionRadioactivity RECOMMENDED, but REQUIRED if
ModeOfAdministration is
'bolus-infusion'

number Amount of radioactivity infused into
the patient. This value must be less
than or equal to the total injected
radioactivity
("InjectedRadioactivity"). Units
should be the same as
"InjectedRadioactivityUnits".
InfusionStart RECOMMENDED, but REQUIRED if
ModeOfAdministration is
'bolus-infusion'

```
number Time of start of infusion with respect to
"TimeZero"in the default unit seconds.
```
InfusionSpeed RECOMMENDED, but REQUIRED if
ModeOfAdministration is
'bolus-infusion'

```
number If given, infusion speed.
```
InfusionSpeedUnits RECOMMENDED, but REQUIRED if
ModeOfAdministration is
'bolus-infusion'

```
string Unit of infusion speed (for example,
"mL/s").
```

Key name Requirement Level Data type Description

InjectedVolume RECOMMENDED, but REQUIRED if
ModeOfAdministration is
'bolus-infusion'

```
number Injected volume of the radiotracer in
the unit"mL".
```
Purity RECOMMENDED number Purity of the radiolabeled compound
(between 0 and 100%). Must be a
number greater than or equal to 0 and
less than or equal to 100.

Pharmaceuticals

Key name Requirement Level Data type Description

PharmaceuticalName RECOMMENDED string Name of pharmaceutical
coadministered with tracer.
Corresponds to DICOM Tag (0008,0034)
Intervention Drug Name.
PharmaceuticalDoseAmount RECOMMENDED numberorarrayofnumbers Dose amount of pharmaceutical
coadministered with tracer.
Corresponds to DICOM Tag (0008,0028)
Intervention Drug Dose.
PharmaceuticalDoseUnits RECOMMENDED string Unit format relating to pharmaceutical
dose (for example,"mg"or"mg/kg").
PharmaceuticalDoseRegimen RECOMMENDED string Details of the pharmaceutical dose
regimen. Either adequate description or
short-code relating to regimen
documented elsewhere (for example,
"single oral bolus").


Key name Requirement Level Data type Description

PharmaceuticalDoseTime RECOMMENDED numberorarrayofnumbers Time of administration of
pharmaceutical dose, relative to time
zero. For an infusion, this should be a
vector with two elements specifying the
start and end of the infusion period.
For more complex dose regimens, the
regimen description should be complete
enough to enable unambiguous
interpretation of
"PharmaceuticalDoseTime". Unit
format of the specified pharmaceutical
dose time MUST be seconds.
Corresponds to a combination of
DICOM Tags (0008,0027)Intervention
Drug Stop Timeand (0008,0035)
Intervention Drug Start Time.
Anaesthesia OPTIONAL string Details of anaesthesia used, if any.

Time

Key name Requirement Level Data type Description

TimeZero REQUIRED string Time zero to which all scan and/or
blood measurements have been
adjusted to, in the unit ”hh:mm:ss”.
This should be equal to
"InjectionStart"or"ScanStart".
ScanStart REQUIRED number Time of start of scan with respect to
TimeZeroin the default unit seconds.
InjectionStart REQUIRED number Time of start of injection with respect
to"TimeZero"in the default unit
seconds. This corresponds to DICOM
Tag 0018, 1072Contrast/Bolus Start
Timeconverted to seconds relative to
"TimeZero". Corresponds to DICOM
Tag (0018,1072)Radiopharmaceutical
Start Time.


```
Key name Requirement Level Data type Description
FrameTimesStart REQUIRED arrayofnumbers Start times for all frames relative to
"TimeZero"in default unit seconds.
FrameDuration REQUIRED arrayofnumbers Time duration of each frame in default
unit seconds. This corresponds to
DICOM Tag 0018, 1242Actual Frame
Durationconverted to seconds.
InjectionEnd RECOMMENDED number Time of end of injection with respect to
"TimeZero"in the default unit seconds.
Corresponds to DICOM Tag (0018,1073)
Radiopharmaceutical Stop Time
converted to seconds relative to
TimeZero.
ScanDate ScanDate string Date of scan in the format
"YYYY-MM-DD[Z]". This field is
DEPRECATED, and this metadata
SHOULD be recorded in theacq_time
column of the corresponding ScanDate.
Corresponds to DICOM Tag (0008,0022)
Acquisition Date.
```
We refer to the common principles for the standards for describing dates and timestamps, including possibilities for anonymization (see Units).

```
Reconstruction
```
```
Key name Requirement Level Data type Description
AcquisitionMode REQUIRED string Type of acquisition of the PET data
(for example,"list mode").
ImageDecayCorrected REQUIRED boolean Boolean flag specifying whether the
image data have been decay-corrected.
Must be one of:"true","false".
ImageDecayCorrectionTime REQUIRED number Point in time from which the decay
correction was applied with respect to
"TimeZero"in the default unit seconds.
ReconMethodName REQUIRED string Reconstruction method or algorithm
(for example,"3d-op-osem"). This
partly matches the DICOM Tag
(0054,1103)Reconstruction Method.
```

Key name Requirement Level Data type Description

ReconMethodParameterLabels REQUIRED arrayofstrings Names of reconstruction parameters
(for example,["subsets",
"iterations"]). This partly matches
the DICOM Tag (0054,1103)
Reconstruction Method.
ReconMethodParameterUnits RECOMMENDED, but REQUIRED if
ReconMethodParameterLabelsdoes
not contain"none"

arrayofstrings Unit of reconstruction parameters (for
example,["none", "none"]). This
partly matches the DICOM Tag
(0054,1103)Reconstruction Method.
ReconMethodParameterValues RECOMMENDED, but REQUIRED if
ReconMethodParameterLabelsdoes
not contain"none"

arrayofnumbers Values of reconstruction parameters
(for example,[21, 3]). This partly
matches the DICOM Tag (0054,1103)
Reconstruction Method.
ReconFilterType REQUIRED stringorarrayofstrings Type of post-recon smoothing (for
example,["Shepp"]). This partly
matches the DICOM Tag (0018,1210)
Convolution Kernel.
ReconFilterSize RECOMMENDED, but REQUIRED if
ReconFilterTypeis not"none"

numberorarrayofnumbers Kernel size of post-recon filter (FWHM)
in default units"mm". This partly
matches the DICOM Tag (0018,1210)
Convolution Kernel.
AttenuationCorrection REQUIRED string Short description of the attenuation
correction method used. This
corresponds to DICOM Tag (0054,1101)
Attenuation Correction Method.
ReconMethodImplementationVersion RECOMMENDED string Identification for the software used,
such as name and version.
AttenuationCorrectionMethodReference RECOMMENDED string Reference paper for the attenuation
correction method used.
ScaleFactor RECOMMENDED arrayofnumbers Scale factor for each frame. This field
MUST be defined if the imaging data
(.nii[.gz]) are scaled. If this field is
not defined, then it is assumed that the
scaling factor is 1. Defining this field
when the scaling factor is 1 is
RECOMMENDED, for the sake of
clarity.


Key name Requirement Level Data type Description

ScatterFraction RECOMMENDED arrayofnumbers Scatter fraction for each frame (Units:
0-100%). Corresponds to DICOM Tag
(0054,1323)Scatter Fraction Factor.
DecayCorrectionFactor RECOMMENDED arrayofnumbers Decay correction factor for each frame.
Corresponds to DICOM Tag (0054,1321)
Decay Factor.
DoseCalibrationFactor RECOMMENDED number Multiplication factor used to transform
raw data (in counts/sec) to meaningful
unit (Bq/ml). Corresponds to DICOM
Tag 0054, 1322Dose Calibration
Factor. Corresponds to DICOM Tag
(0054,1322)Dose Calibration Factor.
PromptRate RECOMMENDED arrayofnumbers Prompt rate for each frame (same units
asUnits, for example,"Bq/mL").
SinglesRate RECOMMENDED arrayofnumbers Singles rate for each frame (same units
asUnits, for example,"Bq/mL").
RandomRate RECOMMENDED arrayofnumbers Random rate for each frame (same
units as"Units", for example,
"Bq/mL").

All reconstruction-specific parameters that are not specified, but one wants to include, should go into theReconMethodParameterValuesfield.

Task

If the OPTIONALtask-<label>is used, the following metadata SHOULD be used.

Key name Requirement Level Data type Description

CogPOID RECOMMENDED string CogPOID of the correspondingCogPO
term.
CogAtlasID RECOMMENDED string CogAtlasID of the corresponding
Cognitive AtlasTask term.
TaskDescription RECOMMENDED string Longer description of the task.
Instructions RECOMMENDED string Text of the instructions given to
participants before the recording. This
is especially important in context of
resting state recordings and
distinguishing between eyes open and
eyes closed paradigms.


Key name Requirement Level Data type Description

TaskName RECOMMENDED string Name of the task. No two tasks should
have the same name. The task label
included in the file name is derived from
this"TaskName"field by removing all
non-alphanumeric characters (that is,
all except those matching
[0-9a-zA-Z]). For example
"TaskName" "faces n-back"will
correspond to task labelfacesnback. If
used to denote resting scans, a
RECOMMENDED convention is to use
labels beginning withrest.

Example ( ***_pet.json** )

{
"Manufacturer":"Siemens",
"ManufacturersModelName":"High-Resolution Research Tomograph (HRRT, CTI/Siemens)",
"BodyPart":"Brain",
"Units": "Bq/mL",
"TracerName": "CIMBI-36",
"TracerRadionuclide": "C11",
"TracerMolecularWeight":380.28,
"TracerMolecularWeightUnits":"g/mol",
"InjectedRadioactivity": 573 ,
"InjectedRadioActivityUnits":"MBq",
"InjectedMass":0.62,
"InjectedMassUnits":"ug",
"SpecificRadioactivity":929.6,
"SpecificRadioactivityUnits":"MBq/ug",
"ModeOfAdministration":"bolus",
"MolarActivity":353.51,
"MolarActivityUnits": "GBq/umol",
"MolarActivityMeasTime":"13:04:42",
"TimeZero":"13:04:42",
"ScanStart": 0 ,
"InjectionStart": 0 ,
"FrameTimesStart": [ 0 , 10 , 20 , 30 , 40 , 50 , 60 , 80 , 100 , 120 , 140 , 160 , 180 , 240 , 300 , 360 , 420 , 480 , 540 , 660 , 780 , 900 , 1020 , 1140 , 1260 , 1380 , 1500 , 1800 , 2100 , 2400 , 2700 , 3000 , 3300 , 3600 , 3900 , 4200 , 4500 , 4800 , 5100 , 5400 , 5700 , 6000 , 6300 , 6600 , 6900 ],
"FrameDuration":[ 10 , 10 , 10 , 10 , 10 , 10 , 20 , 20 , 20 , 20 , 20 , 20 , 60 , 60 , 60 , 60 , 60 , 60 , 120 , 120 , 120 , 120 , 120 , 120 , 120 , 120 , 300 , 300 , 300 , 300 , 300 , 300 , 300 , 300 , 300 , 300 , 300 , 300 , 300 , 300 , 300 , 300 , 300 , 300 , 300 ],


"AcquisitionMode": "list mode",
"ImageDecayCorrected": **true** ,
"ImageDecayCorrectionTime": 0 ,
"ReconMethodName": "3D-OSEM-PSF",
"ReconMethodParameterLabels":["subsets","iterations"],
"ReconMethodParameterUnits":["none","none"],
"ReconMethodParameterValues":[ 16 , 10 ],
"ReconFilterType": "none",
"AttenuationCorrection":"[137Cs]transmission scan-based"
}

#### Recommended patient data.

Knudsenetal. 2020(doi:10.1177/0271678X20905433)recommendsrecordingparticipantbodyweight. Ifrecordedonceperparticipant, thesedataSHOULDbeincludedin
the Participants file or as Phenotypic and assessment data.

For example:

participant_id body_weight
sub-01 58
sub-02 96
sub-03 72

If multiple measurements are made, these data SHOULD be included in the Sessions file.

For example:

session_id body_weight
ses-01 58
ses-02 59

### Blood recording data.

Template:

sub-<label>/
[ses-<label>/]
pet/
sub-<label>[_ses-<label>][_task-<label>][_trc-<label>][_rec-<label>][_run-<index>]_recording-<label>_blood.json
sub-<label>[_ses-<label>][_task-<label>][_trc-<label>][_rec-<label>][_run-<index>]_recording-<label>_blood.tsv

Legend:

- Filename entities or directories between square brackets (for example,[_ses-<label>]) are OPTIONAL.


- Some entities may only allow specific values, in which case those values are listed in<>, separated by|.
- _<suffix>means that there are several (>6) valid suffixes for this filename pattern.
- .<extension>means that there are several (>6) valid extensions for this file type.
- [.gz]means that both the unzipped and gzipped versions of the extension are valid.

If collected, blood measurements of radioactivity are be stored in Tabular files and located in thepet/directory along with the corresponding PET data.

The REQUIREDrecordingentity is used to distinguish sampling methods. For example, if an autosampler is used to record continuous blood samples, and manual
measurements are also taken, then the files may have recording labelsautosamplerandmanual, respectively. If the sampling method is unknown, then recording
SHOULD be set asmanual. All blood measurements should be reported according to a single time-scale in relation to time zero defined by the PET data (Figure 1). All
definitions used below are in accordance with Innis et al. 2007 (doi:10.1038/sj.jcbfm.9600493).

Some metadata about the recording MUST be provided in an additional JSON file.

Key name Requirement Level Data type Description

PlasmaAvail REQUIRED boolean Boolean that specifies if plasma
measurements are available. Must be
one of:"true","false".
MetaboliteAvail REQUIRED boolean Boolean that specifies if metabolite
measurements are available. Iftrue,
themetabolite_parent_fraction
column MUST be present in the
corresponding*_blood.tsvfile. Must
be one of:"true","false".
WholeBloodAvail REQUIRED boolean Boolean that specifies if whole blood
measurements are available. Iftrue,
thewhole_blood_radioactivity
column MUST be present in the
corresponding*_blood.tsvfile. Must
be one of:"true","false".
DispersionCorrected REQUIRED boolean Boolean flag specifying whether the
blood data have been
dispersion-corrected. NOTE: not
customary for manual samples, and
hence should be set tofalse. Must be
one of:"true","false".
WithdrawalRate RECOMMENDED number The rate at which the blood was
withdrawn from the subject. The unit
of the specified withdrawal rate should
be in"mL/s".


Key name Requirement Level Data type Description

TubingType RECOMMENDED string Description of the type of tubing used,
ideally including the material and
(internal) diameter.
TubingLength RECOMMENDED number The length of the blood tubing, from
the subject to the detector in meters.
DispersionConstant RECOMMENDED number External dispersion time constant
resulting from tubing in default unit
seconds.
Haematocrit RECOMMENDED number Measured haematocrit, meaning the
volume of erythrocytes divided by the
volume of whole blood.
BloodDensity RECOMMENDED number Measured blood density. Unit of blood
density should be in"g/mL".

The following metadata SHOULD or MUST be provided if corresponding flags aretrue.

Key name Requirement Level Data type Description

PlasmaFreeFraction RECOMMENDED ifPlasmaAvailis
true

number Measured free fraction in plasma,
meaning the concentration of free
compound in plasma divided by total
concentration of compound in plasma
(Units: 0-100%). Must be a number
greater than or equal to 0 and less than
or equal to 100.
PlasmaFreeFractionMethod RECOMMENDED ifPlasmaAvailis
true

```
string Method used to estimate free fraction.
```
MetaboliteMethod REQUIREDifMetaboliteAvailistrue string Method used to measure metabolites.
MetaboliteRecoveryCorrectionApplied REQUIREDifMetaboliteAvailistrue boolean Metabolite recovery correction from the
HPLC, for tracers where it changes with
time postinjection. Iftrue, the
hplc_recovery_fractionscolumn
MUST be present in the corresponding
*_blood.tsvfile. Must be one of:
"true","false".

The following columns are defined for_blood.tsvfiles. Thetimecolumn MUST always be the first column.


Column name Requirement Level Data type Description

time REQUIRED number Time, in seconds, relative toTimeZero
defined by the*_pet.json. For
example, 5.
plasma_radioactivity OPTIONAL, but REQUIRED if
PlasmaAvailistrue

number Radioactivity in plasma, in unit of
plasma radioactivity (for example,
kBq/mL).
metabolite_parent_fraction OPTIONAL, but REQUIRED if
MetaboliteAvailistrue

number Parent fraction of the radiotracer (0-1).
Must be a number greater than or equal
to 0 and less than or equal to 1.
metabolite_polar_fraction OPTIONAL, but REQUIRED if
MetaboliteAvailistrue

number Polar metabolite fraction of the
radiotracer (0-1). Must be a number
greater than or equal to 0 and less than
or equal to 1.
hplc_recovery_fractions OPTIONAL, but REQUIRED if
MetaboliteRecoveryCorrectionApplied
istrue

number HPLC recovery fractions (the fraction
of activity that gets loaded onto the
HPLC).
whole_blood_radioactivity OPTIONAL, but REQUIRED if
WholeBloodAvailistrue

number Radioactivity in whole blood samples,
in unit of radioactivity measurements
in whole blood samples (for example,
kBq/mL).
Additional Columns NOT ALLOWED n/a Additional columns are not allowed.

As with all tabular files, additional columns MAY be defined in_blood.json. For clarity, it is RECOMMENDED to include the above column definitions in_blood.json,
as shown in the following example.

#### Example blood data

***_recording-manual_blood.json** :

{
"PlasmaAvail": **true** ,
"WholeBloodAvail": **true** ,
"MetaboliteAvail": **true** ,
"MetaboliteMethod": "HPLC",
"MetaboliteRecoveryCorrectionApplied": **false** ,
"DispersionCorrected": **false** ,
"time": {
"Description":"Time in relation to time zero defined by the _pet.json",
"Units": "s"


##### },

"plasma_radioactivity":{
"Description":"Radioactivity in plasma samples. Measured using COBRA counter.",
"Units": "kBq/mL"
},
"whole_blood_radioactivity": {
"Description":"Radioactivity in whole blood samples. Measured using COBRA counter.",
"Units": "kBq/mL"
},
"metabolite_parent_fraction": {
"Description":"Parent fraction of the radiotracer.",
"Units": "arbitrary"
},
"metabolite_polar_fraction": {
"Description":"Polar metabolite fraction of the radiotracer.",
"Units": "arbitrary"
},
"metabolite_lipophilic_fraction": {
"Description":"Lipophilic metabolite fraction of the radiotracer.",
"Units": "arbitrary"
}
}

***_recording-manual_blood.tsv** :

time plasma_radioactivity whole_blood_radioactivity metabolite_parent_fraction metabolite_polar_fraction
0 0 0 1 0
145 43.31 33.79 0.5749 0.1336
292 48.96 37.42 0.3149 0.2746
602 39.84 32.05 0.1469 0.3548
1248 37.38 31.52 0.073 0.444
1785 36.40 28.83 0.078 0.429
2390 33.13 26.32 0.061 0.453
3059 30.83 25.22 0.049 0.473
4196 27.28 21.98 0.036 0.503
5407 22.70 19.49 0.032 0.523
7193 19.71 15.70 0.02 0.559


## Microscopy

Support for Microscopy was developed as a BIDS Extension Proposal.

Please see Citing BIDS on how to appropriately credit this extension when referring to it in the context of the academic literature.

MicroscopydatasetsformattedusingthisspecificationareavailableontheBIDSexamplesrepositoryandcanbeusedforpracticalguidancewhencuratinganewdataset.

Further Microscopy datasets are available:

- In PNG format:data_axondeepseg_sem
- In OME-TIFF format:Broca's Area Light-Sheet Microscopy

### Microscopy imaging data

Template:

sub-<label>/
[ses-<label>/]
micr/
sub-<label>[_ses-<label>]_sample-<label>[_acq-<label>][_stain-<label>][_run-<index>][_chunk-<index>]_<suffix>.<extension>
sub-<label>[_ses-<label>]_sample-<label>[_acq-<label>][_stain-<label>][_run-<index>][_chunk-<index>]_<suffix>.json

Legend:

- Filename entities or directories between square brackets (for example,[_ses-<label>]) are OPTIONAL.
- Some entities may only allow specific values, in which case those values are listed in<>, separated by|.
- _<suffix>means that there are several (>6) valid suffixes for this filename pattern.
- .<extension>means that there are several (>6) valid extensions for this file type.
- [.gz]means that both the unzipped and gzipped versions of the extension are valid.

Microscopy data MUST be stored in themicrdirectory.


#### File formats.

The Microscopy community uses a variety of formats for storing raw data, and there is no single standard that all researchers agree on. However, a standardized
file structure has been developed by theOpen Microscopy Environmentfor whole-slide imaging with theOME-TIFF file specifications. The OME-TIFF file allows for
multi-page TIFF files to store multiple image planes and supports multi-resolution pyramidal tiled images. An OME-XML data block is also embedded inside the file’s
header. Further, OME-ZARR (sometimes referredto as OME-NGFF or NGFF) has been developed to provide improved access and storage for large data via chunked and
compressed N-dimensional arrays.

The BIDS standard accepts microscopy data in a number of file formats to accommodate datasets stored in 2D image formats and whole-slide imaging formats, to
accommodate lossless and lossy compression, and to avoid unnecessary conversions of the original data from a non-tiled to a tiled format, or vice-versa.

Microscopy raw data MUST be stored in one of the following formats:

- Portable Network Graphics(.png)
- Tag Image File Format(.tif)
- OME-TIFF(.ome.tiffor standard TIFF files or.ome.btfforBigTIFFfiles)
- OME-ZARR/NGFF(.ome.zarrdirectories)

If different from PNG, TIFF, OME-TIFF, or OME-ZARR, the original unprocessed data in the native format MAY be stored in the/sourcedatadirectory.

#### Modality suffixes.

Microscopy data currently support the following imaging modalities:

```
Name suffix Description
2-photon excitation microscopy 2PE 2-photon excitation microscopy imaging data
Bright-field microscopy BF Bright-field microscopy imaging data
Coherent anti-Stokes Raman spectroscopy CARS Coherent anti-Stokes Raman spectroscopy imaging
data
Confocal microscopy CONF Confocal microscopy imaging data
Differential interference contrast microscopy DIC Differential interference contrast microscopy imaging
data
Dark-field microscopy DF Dark-field microscopy imaging data
Fluorescence microscopy FLUO Fluorescence microscopy imaging data
Multi-photon excitation microscopy MPE Multi-photon excitation microscopy imaging data
Nonlinear optical microscopy NLO Nonlinear optical microscopy imaging data
Optical coherence tomography OCT Optical coherence tomography imaging data
Phase-contrast microscopy PC Phase-contrast microscopy imaging data
Polarized-light microscopy PLI Polarized-light microscopy imaging data
Scanning electron microscopy SEM Scanning electron microscopy imaging data
Selective plane illumination microscopy SPIM Selective plane illumination microscopy imaging data
```

```
Name suffix Description
Super-resolution microscopy SR Super-resolution microscopy imaging data
Transmission electron microscopy TEM Transmission electron microscopy imaging data
Micro-CT uCT Micro-CT imaging data
```
#### Filename entities.

In the context of Microscopy, a session (ses-<label>) can refer to all the acquisitions between the start and the end of an imaging experiment for ex vivo imaging, or a
subject lab visit for biopsy procedure and/or in vivo imaging. Consistent with other data types in BIDS, the session entity is optional.

Thesample-<label>entity is REQUIRED for Microscopy data and is used to distinguish between different samples from the same subject. The label MUST be unique
per subject and is RECOMMENDED to be unique throughout the dataset.

For example: Three brain slices (sample-01tosample-03) extracted from subjectsub-01, imaged by scanning electron microscopy (SEM) in PNG format

```
sub-01/
micr/
sub-01_sample-01_SEM.png
sub-01_sample-02_SEM.png
sub-01_sample-03_SEM.png
sub-01_SEM.json
```
In this example, the JSON metadata is common for all samples ofsub-01. JSON metadata may be defined per subject or per sample as appropriate, as per the inheritance
principle.

Theacq-<label>entity corresponds to a custom label that MAY be used to distinguish a different set of parameters used for acquiring the same modality. For example,
two images of the same sample acquired by bright-field microscopy (BF) in PNG format at different magnification of 40x and 60x. In such case two files could have the
following names:sub-01_sample-01_acq-40x_BF.pngandsub-01_sample-01_acq-60x_BF.png, however the user is free to choose any other label as long as they are
consistent across subjects and sessions.

Thestain-<label>entity MAY be used to distinguish image files from the same sample using different stains or antibodies for contrast enhancement.

Forexample: Onebrainslice(sample-01)extractedfromsubjectsub-01withthreestains(stain-01,stain-02andstain-03)inthreeseparatefiles, imagedbyselective
plane illumination microscopy (SPIM) in OME-TIFF format

```
sub-01/
micr/
sub-01_sample-01_stain-01_SPIM.ome.tif
sub-01_sample-01_stain-01_SPIM.json
sub-01_sample-01_stain-02_SPIM.ome.tif
sub-01_sample-01_stain-02_SPIM.json
sub-01_sample-01_stain-03_SPIM.ome.tif
sub-01_sample-01_stain-03_SPIM.json
```

In this example, the entity stain is used to distinguish images with different stains in separate files from the same sample. In the case where a single file contains different
staining in each channel, thestain-<label>is omitted.

StainsSHOULDbeindicatedinthe"SampleStaining"keyinthesidecarJSONfile,althoughthelabelmaybedifferent. DescriptionofantibodiesSHOULDalsobeindicated
in"SamplePrimaryAntibodies"and/or"SampleSecondaryAntobodies"as appropriate.

Ifmorethanonerunofthesamesample,acquisitionandstainareacquiredduringthesamesession,therun-<index>entityMUSTbeused:_run-1,_run-2,_run-3,and
so on. If only one run was acquired therun-<index>can be omitted.

Thechunk-<index>entity is used when multiples regions (2D images or 3D volumes files) of the same physical sample are imaged with different fields of view, regardless
if they overlap or not.

In some cases, the chunks can be ”ordered” and, for example, correspond to the displacement of the microscope stage. In other cases, the chunks can be different images
of the same sample with no explicit spatial relation between them.

Examples of different chunks configurations can be seen in Figure 1.

Figure 1: Examples of chunks configurations.

- a) ordered 2D chunks without overlap,
- b) ordered 2D chunks with overlap,
- c) unordered 2D chunks with and without overlap,
- d) and e) ordered 2D chunks on different 3D planes,
- f) ordered 3D chunks.

For example: Four chunks (chunk-01tochunk-04) from the same brain sample (sample-01) of subjectsub-01, imaged by confocal microscopy (CONF) in OME-TIFF
format

```
sub-01/
```

```
micr/
sub-01_sample-01_chunk-01_CONF.ome.tif
sub-01_sample-01_chunk-01_CONF.json
sub-01_sample-01_chunk-02_CONF.ome.tif
sub-01_sample-01_chunk-02_CONF.json
sub-01_sample-01_chunk-03_CONF.ome.tif
sub-01_sample-01_chunk-03_CONF.json
sub-01_sample-01_chunk-04_CONF.ome.tif
sub-01_sample-01_chunk-04_CONF.json
```
Theindexnumbercanbeassignedarbitrarilyand, inthecaseof”ordered”chunks, thechunks’relativepositions(intermsofscalingandtranslation)SHOULDbedefined
by an affine transformation matrix in the JSON sidecar file of each chunk, as described in Chunk Transformations.

In this example, the JSON metadata is different for each chunk ofsub-01_sample-01. JSON metadata may be defined per sample or per chunk as appropriate, as per the
inheritance principle.

In microscopy, many pyramidal file formats store multiple resolutions for the same acquisition. In the case where a multiple resolutions file format is converted to single
resolution file format, only the higher resolution file is present in the raw data. Lower resolutions files MUST be placed under thederivativesdirectory and use the
res-<label>entity.

For example:

```
my_dataset/
derivatives/
downsampled/
sub-01/
micr/
sub-01_sample-01_res-4x_TEM.png
sub-01_sample-01_res-4x_TEM.json
sub-01/
micr/
sub-01_sample-01_TEM.png
sub-01_sample-01_TEM.json
```
See Preprocessed, coregistered and/or resampled volumes for details.

#### Microscopy metadata (Sidecar JSON).

Microscopy data MUST be described by metadata fields, stored in sidecar JSON files.

Device Hardware


Key name Requirement Level Data type Description

Manufacturer RECOMMENDED string Manufacturer of the equipment that
produced the measurements.
ManufacturersModelName RECOMMENDED string Manufacturer’s model name of the
equipment that produced the
measurements.
DeviceSerialNumber RECOMMENDED string The serial number of the equipment
that produced the measurements. A
pseudonym can also be used to prevent
the equipment from being identifiable,
so long as each pseudonym is unique
within the dataset.
StationName RECOMMENDED string Institution defined name of the machine
that produced the measurements.
SoftwareVersions RECOMMENDED string Manufacturer’s designation of software
version of the equipment that produced
the measurements.
InstitutionName RECOMMENDED string The name of the institution in charge of
the equipment that produced the
measurements.
InstitutionAddress RECOMMENDED string The address of the institution in charge
of the equipment that produced the
measurements.
InstitutionalDepartmentName RECOMMENDED string The department in the institution in
charge of the equipment that produced
the measurements.

Image Acquisition


Key name Requirement Level Data type Description

PixelSize REQUIRED arrayofnumbers A 2- or 3-number array of the physical
size of a pixel, either[PixelSizeX,
PixelSizeY]or[PixelSizeX,
PixelSizeY, PixelSizeZ], where X is
the width, Y the height and Z the depth.
If the file format is OME-TIFF, these
values need to be consistent with
PhysicalSizeX,PhysicalSizeYand
PhysicalSizeZOME metadata fields,
after converting inPixelSizeUnits
according toPhysicalSizeXunit,
PhysicalSizeYunitand
PhysicalSizeZunitOME fields.
PixelSizeUnits REQUIRED string Unit format of the specified
"PixelSize". MUST be one of:"mm"
(millimeter),"um"(micrometer) or"nm"
(nanometer). Must be one of:"mm",
"um","nm".
Immersion OPTIONAL string Lens immersion medium. If the file
format is OME-TIFF, the value MUST
be consistent with theImmersionOME
metadata field.
NumericalAperture OPTIONAL number Lens numerical aperture (for example:
1.4). If the file format is OME-TIFF,
the value MUST be consistent with the
LensNAOME metadata field. Must be a
number greater than 0.
Magnification OPTIONAL number Lens magnification (for example: 40 ). If
the file format is OME-TIFF, the value
MUST be consistent with the
"NominalMagnification"OME
metadata field. Must be a number
greater than 0.
ImageAcquisitionProtocol OPTIONAL string Description of the image acquisition
protocol or ImageAcquisitionProtocol
(for example fromprotocols.io).
OtherAcquisitionParameters OPTIONAL string Description of other relevant image
acquisition parameters.


Sample

Key name Requirement Level Data type Description

BodyPart RECOMMENDED string Body part of the organ / body region
scanned. FromDICOM Body Part
Examined(for example"BRAIN").
BodyPartDetails RECOMMENDED string Additional details about body part or
location (for example:"corpus
callosum").
BodyPartDetailsOntology OPTIONAL string BodyPartDetailsOntology of ontology
used for BodyPartDetails (for example:
"https://www.ebi.ac.uk/ols/ontologies/uberon").
SampleEnvironment RECOMMENDED string Environment in which the sample was
imaged. MUST be one of:"in vivo",
"ex vivo"or"in vitro". Must be one
of:"in vivo","ex vivo","in vitro".
SampleEmbedding OPTIONAL string Description of the tissue sample
embedding (for example:"Epoxy
resin").
SampleFixation OPTIONAL string Description of the tissue sample fixation
(for example:"4% paraformaldehyde,
2% glutaraldehyde").
SampleStaining RECOMMENDED stringorarrayofstrings Description(s) of the tissue sample
staining (for example:"Osmium"). MAY
be an array of strings if different stains
are used in each channel of the file (for
example:["LFB", "PLP"]).
SamplePrimaryAntibody RECOMMENDED stringorarrayofstrings Description(s) of the primary antibody
used for immunostaining. Either an
RRIDor the name, supplier and
catalogue number of a commercial
antibody. For non-commercial
antibodies either anRRIDor the
host-animal and immunogen used (for
examples:"RRID:AB_2122563"or
"Rabbit anti-Human HTR5A
Polyclonal Antibody, Invitrogen,
Catalog # PA1-2453"). MAY be an
array of strings if different antibodies
are used in each channel of the file.


Key name Requirement Level Data type Description

SampleSecondaryAntibody RECOMMENDED stringorarrayofstrings Description(s) of the secondary
antibody used for immunostaining.
Either anRRIDor the name, supplier
and catalogue number of a commercial
antibody. For non-commercial
antibodies either anRRIDor the
host-animal and immunogen used (for
examples:"RRID:AB_228322"or"Goat
anti-Mouse IgM Secondary
Antibody, Invitrogen, Catalog #
31172"). MAY be an array of strings if
different antibodies are used in each
channel of the file.
SliceThickness OPTIONAL number Slice thickness of the tissue sample in
the unit micrometers ("um") (for
example: 5 ). Must be a number greater
than 0.
TissueDeformationScaling OPTIONAL number Estimated deformation of the tissue,
given as a percentage of the original
tissue size (for examples: for a
shrinkage of 3%, the value is 97 ; and for
an expansion of 100%, the value is 200 ).
Must be a number greater than 0.
SampleExtractionProtocol OPTIONAL string Description of the sample extraction
protocol or SampleExtractionProtocol
(for example fromprotocols.io).
SampleExtractionInstitution OPTIONAL string The name of the institution in charge of
the extraction of the sample, if different
from the institution in charge of the
equipment that produced the image.

Chunk Transformations

Chunk transformations metadata describes the spatial relation between chunks of the same sample in an implicit coordinate system.

- The source frame of reference is the frame of reference of the associated image.
- The target frame of reference is the implicit coordinate system of the transform.
- The target frame of reference has the same units as thePixelSizeUnitsmetadata.


- The chunk transformation is described by 2 metadata fields: an affine transformation matrix and a description of the axis of the matrix.
- Other transformations should be described in derivatives.

Key name Requirement Level Data type Description

ChunkTransformationMatrix RECOMMENDED ifchunk-<index>is
used in filenames

arrayofarrays 3x3 or 4x4 affine transformation matrix
describing spatial chunk
transformation, for 2D and 3D
respectively (for examples:[[2, 0,
0], [0, 3, 0], [0, 0, 1]]in 2D for
2x and 3x scaling along the first and
second axis respectively; or[[1, 0, 0,
0], [0, 2, 0, 0], [0, 0, 3, 0],
[0, 0, 0, 1]]in 3D for 2x and 3x
scaling along the second and third axis
respectively). Note that non-spatial
dimensions like time and channel are
not included in the transformation
matrix.
ChunkTransformationMatrixAxis REQUIRED if
ChunkTransformationMatrixis present

```
arrayofstrings Describe the axis of the
ChunkTransformationMatrix (for
examples:["X", "Y"]or["Z", "Y",
"X"]).
```
An example of chunk transformations JSON metadata forchunk-01andchunk-05of Figure 2 is shown below:

Figure 2: Example figure for chunks transformations.

In this example, there is no scaling andchunk-01is at the origin.chunk-05is translated by 5 um alongX+and by 3 um alongY+.

***_chunk-01_<suffix>.json** :

{
"PixelSize": [ 1 , 1 ],
"PixelSizeUnits":"um",


"ChunkTransformationMatrix": [[ 1 , 0 , 0 ],
[ 0 , 1 , 0 ],
[ 0 , 0 , 1 ]],
"ChunkTransformationMatrixAxis":["X", "Y"]
}

***_chunk-05_<suffix>.json** :

{
"PixelSize": [ 1 , 1 ],
"PixelSizeUnits":"um",
"ChunkTransformationMatrix": [[ 1 , 0 , 5 ],
[ 0 , 1 , 3 ],
[ 0 , 0 , 1 ]],
"ChunkTransformationMatrixAxis":["X", "Y"]
}

Example of sidecar JSON file ( ***_<suffix>.json** )

{
"Manufacturer": "Hamamatsu",
"ManufacturersModelName": "C9600-12",
"PixelSize": [0.23,0.23],
"PixelSizeUnits":"um",
"Magnification": 40 ,
"BodyPart": "BRAIN",
"BodyPartDetails":"corpus callosum",
"SampleEnvironment": "ex vivo",
"SampleFixation":"4% paraformaldehyde, 2% glutaraldehyde",
"SampleStaining":"LFB",
"SliceThickness": 5 ,
"TissueDeformationScaling": 97
}

### Required Samples file

For Microscopy data, the Samples filesamples.tsvis REQUIRED and its associated sidecarsamples.jsonfile is RECOMMENDED.

Additional optional columns MAY be used to describe other samples’ attributes.


### Recommended Participants data

For Microscopy data, we RECOMMEND to make use of the columnsspecies,strainandstrain_rridin the Participants file when applicable.

Additional optional columns MAY be used to describe other subjects’ attributes.

participants.tsvexample:

participant_id species strain strain_rrid
sub-01 mus musculus C57BL/6J RRID:IMSR_JAX:000664
sub-02 mus musculus C57BL/6J RRID:IMSR_JAX:000664

participants.jsonexample:

{
"species":{
"Description":"binomial species name from the NCBI Taxonomy (https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi)"
},
"strain":{
"Description":"name of the strain of the species"
},
"strain_rrid":{
"Description":"research resource identifier (RRID) of the strain (https://scicrunch.org/resources/Organisms/search)"
}
}

### Photos of the samples (*_photo.<extension>)

Photosofthetissuesample, overviewmicroscopyscansorblockfaceimagesfromcuttingMAYbeincludedforvisualizationoflargesamplesortoindicatethelocationof
chunks in a sample.

Template:

sub-<label>/
[ses-<label>/]
micr/
sub-<label>[_ses-<label>]_sample-<label>[_acq-<label>]_photo.<extension>
sub-<label>[_ses-<label>]_sample-<label>[_acq-<label>]_photo.json

Legend:

- Filename entities or directories between square brackets (for example,[_ses-<label>]) are OPTIONAL.
- Some entities may only allow specific values, in which case those values are listed in<>, separated by|.
- _<suffix>means that there are several (>6) valid suffixes for this filename pattern.


- .<extension>means that there are several (>6) valid extensions for this file type.
- [.gz]means that both the unzipped and gzipped versions of the extension are valid.

The file<extension>for photos MUST be either.jpg,.pngor.tif.

Theacq-<label>entity MAY be used to indicate acquisition of different photos of the same sample.

For example:

```
sub-01/
ses-01/
micr/
sub-01_ses-01_sample-01_acq-1_photo.jpg
sub-01_ses_01_sample-01_acq-2_photo.jpg
```
Photo data MAY be accompanied by a JSON file containing the following fields. TheIntendedForfield is used to link the photo to specific image(s) it was acquired for.

Key name Requirement Level Data type Description

PhotoDescription OPTIONAL string Description of the photo.
IntendedFor OPTIONAL stringorarray The paths to files for which the
associated file is intended to be used.
Contains one or more IntendedFor.
Using forward-slash separated paths
relative to the participant subdirectory
is IntendedFor. This field is OPTIONAL,
in case the photos do not correspond to
any particular images, it does not have
to be filled.

For example:sub-01_ses-01_sample-01_acq-1_photo.json

{
"PhotoDescription":"After clearing",
"IntendedFor":[
"ses-01/micr/sub-01_ses-01_sample-01_run-1_chunk-01_SPIM.ome.tif",
"ses-01/micr/sub-01_ses-01_sample-01_run-1_chunk-02_SPIM.ome.tif",
"ses-01/micr/sub-01_ses-01_sample-01_run-1_chunk-03_SPIM.ome.tif",
"ses-01/micr/sub-01_ses-01_sample-01_run-1_chunk-04_SPIM.ome.tif"
]
}

Below is an example of a spinal cord SEM overview, modified from Zaimi et al., 2018.doi:10.1038/s41598-018-22181-4.


sub-01_sample-01_photo.jpg



## Near-Infrared Spectroscopy

Support for Near-Infrared Spectroscopy (NIRS) was developed as a BIDS Extension Proposal. Please see Citing BIDS on how to appropriately credit this extension when
referring to it in the context of the academic literature.

Severalexample NIRS datasetshave been formatted using this specification and can be used for practical guidance when curating a new dataset.

### NIRS recording data

Template:

sub-<label>/
[ses-<label>/]
nirs/
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>]_channels.json
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>]_channels.tsv
sub-<label>[_ses-<label>][_acq-<label>]_coordsystem.json
sub-<label>[_ses-<label>][_acq-<label>]_optodes.json
sub-<label>[_ses-<label>][_acq-<label>]_optodes.tsv
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>]_nirs.json
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>]_nirs.snirf
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>]_events.json
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>]_events.tsv

Legend:

- Filename entities or directories between square brackets (for example,[_ses-<label>]) are OPTIONAL.
- Some entities may only allow specific values, in which case those values are listed in<>, separated by|.
- _<suffix>means that there are several (>6) valid suffixes for this filename pattern.
- .<extension>means that there are several (>6) valid extensions for this file type.
- [.gz]means that both the unzipped and gzipped versions of the extension are valid.


Only the Shared Near Infrared Spectroscopy Format (SNIRF) file specification is supported in BIDS. The SNIRF specification supports one or more NIRS datasets to be
stored in a single.snirffile. However, to be BIDS compatible, each SNIRF file MUST contain only a single run. A limited set of fields from the SNIRF specification
are replicated in the BIDS specification. This redundancy allows the data to be easily parsed by humans and machines that do not have a SNIRF reader at hand, which
improves findability and tooling development.

Raw NIRS data in the native format, if different from SNIRF, can also be stored in the/sourcedatadirectory along with code to convert the data to SNIRF in the/code
directory. The unprocessed raw data should be stored in the manufacturer’s format before any additional processing or conversion is applied. Retaining the native file
format is especially valuable in a case when conversion elicits the loss of crucial metadata unique to specific manufacturers and NIRS systems.

#### Terminology

ForproperdocumentationofNIRSrecordingmetadata,itisimportanttounderstandthedifferencebetweenaSource,Detector,andChannelasthesearedefineddifferently
to other modalities, such as EEG. The following definitions apply in this document:

- Source - A light emitting device, sometimes called a transmitter.
- Detector - A photoelectric transducer, sometimes called a receiver.
- Optode - Refers to either a source or detector.
- Channel - A paired coupling of a source and a detector with one specific wavelength of light. It is common for a single Source-Detector pair to result in two or more
    channels with different wavelengths.

#### Sidecar JSON (*_nirs.json)

It is common within the NIRS community for researchers to build their own caps and optode holders to position their sources and detectors, or for optodes to be directly
attachedtothescalpwithadhesive. Tofacilitatedescriptionofthewidevarietyofpossibleconfigurations,severalfieldsareRECOMMENDEDwithinthe*_nirs.jsonfile.
Additionally, in certain situations, reserved keywords MUST be used. When custom modifications are made to a commercially available cap or a custom cap is used, then
the reserved keywordcustomMUST be used for theCapManufacturersModelNamefield. When a custom-made cap is used, that is, no (modified) commercially available
cap, the reserved keywordcustomMUST be used in theCapManufacturerfield. If no cap is used, the reserved keywordnoneMUST be used in theCapManufacturerand
CapManufacturersModelNamefield. The use ofNIRSPlacementSchemeis RECOMMENDED when no cap or a customized cap is used, and describes the positioning of the
optodes. This field may also contain a reference to a file providing a graphical depiction of the cap, for example a PDF file, a photo, or a bitmap drawing. If the referred
file is not specified in BIDS, it MAY be placed in the/sourcedatadirectory. To clarify the usage and interaction of these fields, the following examples are provided:

- If a commercial cap such as EasyCap actiCAP 64 Ch Standard-2 was used:JSON "CapManufacturer": "EasyCap", "CapManufacturersModelName":
    "actiCAP 64 Ch Standard-2", "NIRSPlacementScheme": "10-20"
- If an Artinis Medical Systems cap with custom positions, as may be done by cutting custom holes in the cap, was used:JSON "CapManufacturer": "Artinis
    Medical Systems", "CapManufacturersModelName": "headcap with print, size L, it was modified by adding holes for the optodes according
    to the NIRSPlacementScheme and optode_layout.pdf", "NIRSPlacementScheme": "see optode_layout.pdf: 2 groups over the left and right
    dlPFC, 2 groups over the left and right PPC, 1 group over the left M1 and PMC"
- If a completely custom cap was knitted:JSON "CapManufacturer": "custom", "CapManufacturersModelName": "custom knitted cap with holes
    for optodes according to the NIRSPlacementScheme and optode_knitted_layout.jpg", "NIRSPlacementScheme": "see optode_knitted_layout.jpg:
    2 groups over the left and right dlPFC, 2 groups over the left and right PPC."


- IfnocapwasusedandoptodesweretapedtothescalpatpositionsCz,C1andC2:JSON "CapManufacturer": "none", "CapManufacturersModelName":
    "none", "NIRSPlacementScheme": ["Cz", "C1", "C2"],In these cases additional information regarding channels and optodes SHOULD be placed in
    *_channels.tsvand*_optodes.tsvfiles.

Closely spaced or short-separation source-detector pairs are often included in NIRS measurements to obtain a measure of systemic, rather than neural, activity. These
source-detectorpairsarereferredtoasshortchannels. Thereisvariationinhowmanufacturersimplementtheseshortchannels,someusespecialisedsourcesordetectors,
and the placement mechanisms vary. It is beyond the scope of the BIDS specification to define what constitutes a short channel, and detailed characteristics of channels
may be stored within the SNIRF file (for example, in thesourcePowerfield). However, to improve searchability and ease of access for users, it is useful to know if short
channelswereincludedintheNIRSmeasurements;thepresenceofshortchannelsisisstoredinthefieldShortChannelCount. IfthefieldShortChannelCountispopulated,
then the optional columnshort_channelmay be used in*_channels.tsvto describe which channels were specified as short.

Generic fields: For consistency between studies and institutions, we encourage users to extract the values of these fields from the actual raw data. Whenever possible,
please avoid using ad hoc wording.

Key name Requirement Level Data type Description

TaskName REQUIRED string Name of the task. No two tasks should
have the same name. The task label
included in the file name is derived from
this"TaskName"field by removing all
non-alphanumeric characters (that is,
all except those matching
[0-9a-zA-Z]). For example
"TaskName" "faces n-back"will
correspond to task labelfacesnback.
InstitutionName RECOMMENDED string The name of the institution in charge of
the equipment that produced the
measurements.
InstitutionAddress RECOMMENDED string The address of the institution in charge
of the equipment that produced the
measurements.
Manufacturer RECOMMENDED string Manufacturer of the equipment that
produced the measurements.
ManufacturersModelName RECOMMENDED string Manufacturer’s model name of the
equipment that produced the
measurements.
SoftwareVersions RECOMMENDED string Manufacturer’s designation of software
version of the equipment that produced
the measurements.
TaskDescription RECOMMENDED string Longer description of the task.
Instructions RECOMMENDED string Text of the instructions given to
participants before the recording.


Key name Requirement Level Data type Description

CogAtlasID RECOMMENDED string CogAtlasID of the corresponding
Cognitive AtlasTask term.
CogPOID RECOMMENDED string CogPOID of the correspondingCogPO
term.
DeviceSerialNumber RECOMMENDED string The serial number of the equipment
that produced the measurements. A
pseudonym can also be used to prevent
the equipment from being identifiable,
so long as each pseudonym is unique
within the dataset.
RecordingDuration RECOMMENDED number Length of the recording in seconds (for
example, 3600 ).
HeadCircumference RECOMMENDED number Circumference of the participant’s head,
expressed in cm (for example, 58 ). Must
be a number greater than 0.
HardwareFilters RECOMMENDED objectofobjectsor"n/a" Object of temporal hardware filters
applied, or"n/a"if the data is not
available. Each key-value pair in the
JSON object is a name of the filter and
an object in which its parameters are
defined as key-value pairs. For example,
{"Highpass RC filter": {"Half
amplitude cutoff (Hz)": 0.0159,
"Roll-off": "6dB/Octave"}}.
SubjectArtefactDescription RECOMMENDED string Freeform description of the observed
subject artefact and its possible cause
(for example,"Vagus Nerve
Stimulator","non-removable
implant"). If this field is set to"n/a", it
will be interpreted as absence of major
source of artifacts except cardiac and
blinks.

Specific NIRS fields that are REQUIRED or may be REQUIRED depending on other metadata values:


Key name Requirement Level Data type Description

SamplingFrequency REQUIRED numberor"n/a" Sampling frequency (in Hz) of all the
data in the recording, regardless of their
type (for example, 2400 ). Sampling
frequency (in Hz) of all the data in the
recording, regardless of their type (for
example, 12 ). If individual channels
have different sampling rates, then the
field here MUST be specified asn/aand
the values MUST be specified in the
sampling_frequencycolumn in
channels.tsv.”)
NIRSChannelCount REQUIRED integer Total number of NIRS channels,
including short channels. Corresponds
to the number of rows inchannels.tsv
with any NIRS type. Must be a number
greater than or equal to 0.
NIRSSourceOptodeCount REQUIRED integer Number of NIRS sources. Corresponds
to the number of rows inoptodes.tsv
with type"source". Must be a number
greater than or equal to 1.
NIRSDetectorOptodeCount REQUIRED integer Number of NIRS detectors. Corresponds
to the number of rows inoptodes.tsv
with type"detector". Must be a
number greater than or equal to 1.
ACCELChannelCount OPTIONAL, but REQUIRED if any
channel type is ACC

integer Number of accelerometer channels.
Must be a number greater than or equal
to 0.
GYROChannelCount OPTIONAL, but REQUIRED if any
channel type is GYRO

integer Number of gyrometer channels. Must
be a number greater than or equal to 0.
MAGNChannelCount OPTIONAL, but REQUIRED if any
channel type is MAGN

```
integer Number of magnetometer channels.
Must be a number greater than or equal
to 0.
```
Specific NIRS fields that SHOULD be present:


Key name Requirement Level Data type Description

CapManufacturer RECOMMENDED string Name of the cap manufacturer (for
example,"EasyCap"). If no cap was
used, such as with optodes that are
directly taped to the scalp, then the
stringnoneMUST be used and the
NIRSPlacementSchemefield MAY be
used to specify the optode placement.
CapManufacturersModelName RECOMMENDED string Manufacturer’s designation of the cap
model (for example,"actiCAP 64 Ch
Standard-2"). If there is no official
model number then a description may
be provided (for example,Headband
with print (S-M)). If a cap from a
manufacturer was modified, then the
field MUST be set tocustom. If no cap
was used, then theCapManufacturer
field MUST benoneand this field MUST
ben/a.”)
SourceType RECOMMENDED string Type of source. Preferably a specific
model/part number is supplied. This is a
freeform description, but the following
keywords are suggested:"LED",
"LASER","VCSEL". If individual
channels have different SourceType,
then the field here should be specified as
”mixed” and this column should be
included in optodes.tsv.
DetectorType RECOMMENDED string Type of detector. This is a free form
description with the following
suggested terms:"SiPD","APD".
Preferably a specific model/part
number is supplied. If individual
channels have differentDetectorType,
then the field here should be specified as
"mixed"and this column should be
included inoptodes.tsv.
ShortChannelCount RECOMMENDED integer The number of short channels. 0
indicates no short channels. Must be a
number greater than or equal to 0.


Key name Requirement Level Data type Description

NIRSPlacementScheme RECOMMENDED stringorarrayofstrings Placement scheme of NIRS optodes.
Either the name of a standardized
placement system (for example,
"10-20") or an array of standardized
position names (for example,["Cz",
"Pz"]). This field should only be used if
a cap was not used. If a standard cap
was used, then it should be specified in
CapManufacturerand
CapManufacturersModelNameand this
field should be set to"n/a"

Example ***_nirs.json**

{
"TaskName":"visual",
"InstitutionName": "Macquarie University. Australian Hearing Hub",
"InstitutionAddress": "6 University Ave, Macquarie University NSW 2109 Australia",
"Manufacturer":"NIRx",
"ManufacturersModelName":"NIRScout",
"TaskDescription": "visual gratings and noise patterns",
"Instructions":"look at the dot in the center of the screen and press the button when it changes color",
"SamplingFrequency":3.7,
"NIRSChannelCount": 56 ,
"NIRSSourceOptodeCount": 16 ,
"NIRSDetectorOptodeCount": 16 ,
"ACCELChannelCount": 0 ,
"SoftwareFilters": "n/a",
"RecordingDuration":233.639,
"HardwareFilters": {"Highpass RC filter":{"Half amplitude cutoff (Hz)":0.0159,"Roll-off": "6dBOctave"}},
"CapManafacturer": "NIRx",
"CapManufacturersModelName":"Headband with print (S-M)",
"NIRSPlacementScheme": "n/a",
}

### Channels description (*_channels.tsv)

Template:


sub-<label>/
[ses-<label>/]
nirs/
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>]_channels.json
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>]_channels.tsv

Legend:

- Filename entities or directories between square brackets (for example,[_ses-<label>]) are OPTIONAL.
- Some entities may only allow specific values, in which case those values are listed in<>, separated by|.
- _<suffix>means that there are several (>6) valid suffixes for this filename pattern.
- .<extension>means that there are several (>6) valid extensions for this file type.
- [.gz]means that both the unzipped and gzipped versions of the extension are valid.

This file is RECOMMENDED as it provides easily searchable information across BIDS datasets. Channels are a pairing of source and detector optodes with a specific
wavelength of light. Unlike in other modalities, not all pairings of optodes correspond to meaningful data and not all pairs have to be recorded or represented in the
data. Note that the source and detector names used in the channel specifications are specified in the*_optodes.tsvfile below. If a*_channels.tsvfile is specified, an
*_optodes.tsvfile MUST be specified as well. The required columns in the*_channels.tsvfile MUST be ordered as listed below.

The BIDS specification supports several types of NIRS devices which output raw data in different forms. The type of measurement is specified in thetypecolumn. For
example, when measurements are taken with a continuous wave (CW) device that saves the data as optical density, thetypeshould beNIRSCWOPTICALDENSITYand the
unitsshould beunitless, this is equivalent to SNIRF data typedOD.

The columns of the channels description table stored in*_channels.tsvare:

Column name Requirement Level Data type Description

name REQUIRED string Label of the channel. This column must
appear first in the file.
type REQUIRED string Type of channel; MUST use the channel
types listed below. Note that the type
MUST be in upper-case. This column
must appear second in the file.For a list
of valid values for this column, see the
type.
source REQUIRED stringor"n/a" Name of the source as specified in the
*_optodes.tsvfile.n/afor channels
that do not contain fNIRS signals (for
example, acceleration). This column
must appear third in the file.


Column name Requirement Level Data type Description

detector REQUIRED stringor"n/a" Name of the detector as specified in the
*_optodes.tsvfile.n/afor channels
that do not contain NIRS signals (for
example, acceleration). This column
must appear fourth in the file.
wavelength_nominal REQUIRED numberor"n/a" Specified wavelength of light in nm.n/a
for channels that do not contain raw
NIRS signals (for example,
acceleration). This field is equivalent to
/nirs(i)/probe/wavelengthsin the
SNIRF specification. This column must
appear fifth in the file.
units REQUIRED string Physical unit of the value represented
in this channel, specified according to
the SI unit symbol and possibly prefix
symbol, or as a derived SI unit (for
example,V, or unitless for changes in
optical densities). For guidelines about
units see the units and units pages. This
column must appear sixth in the file.
sampling_frequency OPTIONAL, but REQUIRED if
SamplingFrequencyisn/ain
_nirs.json

number Sampling rate of the channel in Hz.
This column may appear anywhere in
the file.
orientation_component OPTIONAL, but REQUIRED iftypeis
ACCEL,GYROorMAGN

string Description of the orientation of the
channel. This column may appear
anywhere in the file.Must be one of:
"x","y","z".
wavelength_actual OPTIONAL number Measured wavelength of light in nm.
n/afor channels that do not contain
raw NIRS signals (acceleration). This
field is equivalent to
measurementList.wavelengthActual
in the SNIRF specification. This column
may appear anywhere in the file.
description OPTIONAL string Brief free-text description of the
channel, or other information of
interest. This column may appear
anywhere in the file.


Column name Requirement Level Data type Description

wavelength_emission_actual OPTIONAL number Measured emission wavelength of light
in nm.n/afor channels that do not
contain raw NIRS signals (acceleration).
This field is equivalent to
measurementList.wavelengthEmissionActual
in the SNIRF specification. This column
may appear anywhere in the file.
short_channel OPTIONAL boolean Is the channel designated as short. The
total number of channels listed as short
channels SHOULD be stored in
ShortChannelCountin*_nirs.json.
This column may appear anywhere in
the file.Must be one of:"true",
"false".
status OPTIONAL string Data quality observed on the channel.
A channel is consideredbadif its data
quality is compromised by excessive
noise. If quality is unknown, then a
value ofn/amay be used. Description
of noise type SHOULD be provided in
[status_description]. This column
may appear anywhere in the file.Must
be one of:"good","bad","n/a".
status_description OPTIONAL string Freeform text description of noise or
artifact affecting data quality on the
channel. It is meant to explain why the
channel was declared bad in thestatus
column. This column may appear
anywhere in the file.
Additional Columns OPTIONAL n/a Additional columns are allowed if they
are defined in the associated metadata
file.

#### Restricted keyword list for the channel types

All NIRS channels types MUST correspond to avalid SNIRF data type. Additional channels that are recorded simultaneously with the NIRS device and stored in the
same data file SHOULD be included as well. However, additional channels that are simultaneously recorded with a different device SHOULD be stored according to their
appropriate modality specification. For example, motion data that was simultaneously recorded with a different device should be specified according to BEP029 and not


according to the NIRS data type. Whereas, if the motion data was acquired in with the NIRS device itself, it should be included here with the NIRS data. Any of the
channel types defined in other BIDS specification MAY be used here as well such asACCELorMAGN. As several of these data types are commonly acquired using NIRS
devices they are included as an example at the base of the table. Note that upper-case is REQUIRED.

Keyword Description

NIRSCWAMPLITUDE Continuous wave amplitude measurements. Equivalent to dataType 001 in SNIRF.
NIRSCWFLUORESCENSEAMPLITUDE Continuous wave fluorescence amplitude measurements. Equivalent to dataType
051 in SNIRF.
NIRSCWOPTICALDENSITY Continuous wave change in optical density measurements. Equivalent to
dataTypeLabel dOD in SNIRF.
NIRSCWHBO Continuous wave oxygenated hemoglobin (oxyhemoglobin) concentration
measurements. Equivalent to dataTypeLabel HbO in SNIRF.
NIRSCWHBR Continuous wave deoxygenated hemoglobin (deoxyhemoglobin) concentration
measurements. Equivalent to dataTypeLabel HbR in SNIRF.
NIRSCWMUA Continuous wave optical absorption measurements. Equivalent to dataTypeLabel
mua in SNIRF.
ACCEL Accelerometer channel, one channel for each orientation. An extra column
componentfor the axis of the orientation MUST be added to the*_channels.tsv
file (x, y or z).
GYRO Gyrometer channel, one channel for each orientation. An extra columncomponent
for the axis of the orientation MUST be added to the*_channels.tsvfile (x, y or
z).
MAGN Magnetomenter channel, one channel for each orientation. An extra column
componentfor the axis of the orientation MUST be added to the*_channels.tsv
file (x, y or z).
MISC Miscellaneous

#### Example*_channels.tsv.

Name type source detector wavelength_nominal units
S1-D1 NIRSCWAMPLITUDE A1 Fz 760 V
S1-D1 NIRSCWAMPLITUDE A1 Fz 850 V
S1-D2 NIRSCWAMPLITUDE A1 Cz 760 V
S2-D1 NIRSCWAMPLITUDE A2 Fz 760 V
S3-D4 NIRSCWAMPLITUDE VisS2 VisD4 760 V

### Optode description (*_optodes.tsv)

Template:


sub-<label>/
[ses-<label>/]
nirs/
sub-<label>[_ses-<label>][_acq-<label>]_optodes.json
sub-<label>[_ses-<label>][_acq-<label>]_optodes.tsv

Legend:

- Filename entities or directories between square brackets (for example,[_ses-<label>]) are OPTIONAL.
- Some entities may only allow specific values, in which case those values are listed in<>, separated by|.
- _<suffix>means that there are several (>6) valid suffixes for this filename pattern.
- .<extension>means that there are several (>6) valid extensions for this file type.
- [.gz]means that both the unzipped and gzipped versions of the extension are valid.

File that provides the location and type of optodes. Note that coordinates MUST be expressed in Cartesian coordinates according to the NIRSCoordinateSystem and
NIRSCoordinateSystemUnits fields in*_coordsystem.json. If an*_optodes.tsvfile is specified, a*_coordsystem.jsonfile MUST be specified as well. The order of the
required columns in the*_optodes.tsvfile MUST be as listed below.

The x, y, and z positions are for measured locations, for example, with a polhemus digitizer. If you also have idealized positions, where you wish the optodes to be placed,
thesecanbelistedinthetemplatevalues(forexamplefor”templatepositions”computedonasphere). SNIRFcontainsarraysforboththe3Dand2Dlocationsofdata. In
BIDS the*_optodes.tsvfile MUST contain the 3D locations. Only in case 3D positions are unavailable the 2D locations should be used, setting the z field to ann/avalue.

The columns of the optodes description table stored in*_optodes.tsvare:

Column name Requirement Level Data type Description

name REQUIRED string Name of the optode, must be unique.
This column must appear first in the
file.
type REQUIRED string The type of the optode. This column
must appear second in the file.Must be
one of:"source","detector","n/a".
x REQUIRED numberor"n/a" Recorded position along the x-axis.
"n/a"if not available. This column
must appear third in the file.
y REQUIRED numberor"n/a" Recorded position along the y-axis.
"n/a"if not available. This column
must appear fourth in the file.
z REQUIRED numberor"n/a" Recorded position along the z-axis.
"n/a"if not available. This column
must appear fifth in the file.


Column name Requirement Level Data type Description

template_x OPTIONAL, but REQUIRED ifxisn/a numberor"n/a" Assumed or ideal position along the x
axis. This column may appear
anywhere in the file.
template_y OPTIONAL, but REQUIRED ifyisn/a numberor"n/a" Assumed or ideal position along the y
axis. This column may appear
anywhere in the file.
template_z OPTIONAL, but REQUIRED ifzisn/a numberor"n/a" Assumed or ideal position along the z
axis. This column may appear
anywhere in the file.
description OPTIONAL string Free-form text description of the
optode, or other information of interest.
This column may appear anywhere in
the file.
detector_type OPTIONAL string The type of detector. Only to be used if
the fieldDetectorTypein*_nirs.json
is set tomixed. This column may
appear anywhere in the file.
source_type OPTIONAL string The type of source. Only to be used if
the fieldSourceTypein*_nirs.jsonis
set tomixed. This column may appear
anywhere in the file.
Additional Columns OPTIONAL n/a Additional columns are allowed if they
are defined in the associated metadata
file.

#### Example*_optodes.tsv

name type x y z template_x template_y template_z
A1 source -0.0707 0.0000 -0.0707 -0.07 0.00 0.07
Fz detector 0.0000 0.0714 0.0699 0.0 0.07 0.07
S1 source -0.2707 0.0200 -0.1707 -0.03 0.02 -0.2
D2 detector 0.0022 0.1214 0.0299 0.0 0.12 0.03
VisS2 source -0.1707 0.1200 -0.3707 -0.1 0.1 -0.4
VisD4 detector 0.0322 0.2214 0.2299 0.02 0.22 0.23

### Coordinate System JSON (*_coordsystem.json)

Template:


sub-<label>/
[ses-<label>/]
nirs/
sub-<label>[_ses-<label>][_acq-<label>]_coordsystem.json

Legend:

- Filename entities or directories between square brackets (for example,[_ses-<label>]) are OPTIONAL.
- Some entities may only allow specific values, in which case those values are listed in<>, separated by|.
- _<suffix>means that there are several (>6) valid suffixes for this filename pattern.
- .<extension>means that there are several (>6) valid extensions for this file type.
- [.gz]means that both the unzipped and gzipped versions of the extension are valid.

A*_coordsystem.jsonfile is used to specify the fiducials, the location of anatomical landmarks, and the coordinate system and units in which the position of optodes
and landmarks is expressed. Fiducials are objects with a well-defined location used to facilitate the localization of sensors and co-registration, anatomical landmarks
are locations on a research subject such as the nasion (for a detailed definition see coordinate system appendix). The*_coordsystem.jsonis REQUIRED if the optional
*_optodes.tsvispresent. IfacorrespondinganatomicalMRIisavailable,thelocationsofanatomicallandmarksinthatscanshouldalsobestoredinthe*_T1w.jsonfile
which goes alongside the NIRS data.

Not all NIRS systems provide 3D coordinate information or digitization capabilities. In this case, only x and y are specified and z is"n/a".

General fields:

Key name Requirement Level Data type Description

IntendedFor OPTIONAL stringorarray The paths to files for which the
associated file is intended to be used.
Contains one or more IntendedFor.
Using forward-slash separated paths
relative to the participant subdirectory
is IntendedFor. This identifies the MRI
or CT scan associated with the optodes,
landmarks, and fiducials.

Fields relating to the NIRS optode positions:


Key name Requirement Level Data type Description

NIRSCoordinateSystem REQUIRED string Defines the coordinate system in which
the optode positions are expressed.See
NIRSCoordinateSystem for a list of
restricted keywords for coordinate
systems. If"Other", a definition of the
coordinate system MUST be provided in
NIRSCoordinateSystemDescription.
For a list of valid values for this field,
see the NIRSCoordinateSystem.
NIRSCoordinateUnits REQUIRED string Units of the coordinates of
NIRSCoordinateSystem. Must be one
of:"m","mm","cm","n/a".
NIRSCoordinateProcessingDescription RECOMMENDED string Has any post-processing (such as
projection) been done on the optode
positions (for example,
"surface_projection","n/a").
NIRSCoordinateSystemDescription RECOMMENDED, but REQUIRED if
NIRSCoordinateSystem is ”other”

```
string Free-form text description of the
coordinate system. May also include a
link to a documentation page or paper
describing the system in greater detail.
```
Fields relating to the position of fiducials measured during an NIRS session/run:

Key name Requirement Level Data type Description

FiducialsDescription OPTIONAL string Free-form text description of how the
fiducials such as vitamin-E capsules
were placed relative to anatomical
landmarks, and how the position of the
fiducials were measured (for example,
"both with Polhemus and with T1w
MRI").


Key name Requirement Level Data type Description

FiducialsCoordinates RECOMMENDED objectofarrays Key-value pairs of the labels and 3-D
digitized position of anatomical
landmarks, interpreted following the
"FiducialsCoordinateSystem"(for
example,{"NAS": [12.7,21.3,13.9],
"LPA": [5.2,11.3,9.6], "RPA":
[20.2,11.3,9.1]}). Each array MUST
contain three numeric values
corresponding to x, y, and z axis of the
coordinate system in that exact order.
FiducialsCoordinateUnits RECOMMENDED string Units in which the coordinates that are
listed in the field
"FiducialsCoordinateSystem"are
represented. Must be one of:"m","mm",
"cm","n/a".
FiducialsCoordinateSystem RECOMMENDED string Defines the coordinate system for the
fiducials. Preferably the same as the
"EEGCoordinateSystem". See the
FiducialsCoordinateSystem for a list of
restricted keywords for coordinate
systems. If"Other", provide definition
of the coordinate system in
"FiducialsCoordinateSystemDescription".
For a list of valid values for this field,
see the FiducialsCoordinateSystem.
FiducialsCoordinateSystemDescription RECOMMENDED, but REQUIRED if
FiducialsCoordinateSystem is ”other”

```
string Free-form text description of the
coordinate system. May also include a
link to a documentation page or paper
describing the system in greater detail.
```
Fields relating to the position of anatomical landmarks measured during an NIRS session/run:


Key name Requirement Level Data type Description

AnatomicalLandmarkCoordinates RECOMMENDED objectofarrays Key-value pairs of the labels and 3-D
digitized locations of anatomical
landmarks, interpreted following the
"AnatomicalLandmarkCoordinateSystem"
(for example,{"NAS":
[12.7,21.3,13.9], "LPA":
[5.2,11.3,9.6], "RPA":
[20.2,11.3,9.1]}. Each array MUST
contain three numeric values
corresponding to x, y, and z axis of the
coordinate system in that exact order.
AnatomicalLandmarkCoordinateSystem RECOMMENDED string Defines the coordinate system for the
anatomical landmarks. See the Anatom-
icalLandmarkCoordinateSystem for a
list of restricted keywords for
coordinate systems. If"Other", provide
definition of the coordinate system in
"AnatomicalLandmarkCoordinateSystemDescription".
For a list of valid values for this field,
see the AnatomicalLandmarkCoordi-
nateSystem.
AnatomicalLandmarkCoordinateUnits RECOMMENDED string Units of the coordinates of
"AnatomicalLandmarkCoordinateSystem".
Must be one of:"m","mm","cm","n/a".
AnatomicalLandmarkCoordinateSystemDescriptionRECOMMENDED, but REQUIRED if
NIRSCoordinateSystem is ”other”

```
string Free-form text description of the
coordinate system. May also include a
link to a documentation page or paper
describing the system in greater detail.
```
#### Example*_coordsystem.json

##### {

"NIRSCoordinateSystem":"Other",
"NIRSCoordinateUnits": "mm",
"NIRSCoordinateSystemDescription": "RAS orientation: Origin halfway between LPA and RPA, positive x-axis towards RPA, positive y-axis orthogonal to x-axis through Nasion, z-axis orthogonal to xy-plane, pointing in superior direction.",
"FiducialsDescription":"Optodes and fiducials were digitized with Polhemus, fiducials were recorded as the centre of vitamin E capsules sticked on the left/right pre-auricular and on the nasion, these are also visible on the T1w MRI"
}


## BIDS Derivatives

Derivatives are outputs of common processing pipelines, capturing data and meta-data sufficient for a researcher to understand and (critically) reuse those outputs in
subsequent processing. Standardizing derivatives is motivated by use cases where formalized machine-readable access to processed data enables higher level processing.

The following sections cover additions to and divergences from ”raw” BIDS. Placement and naming conventions for derived datasets are addressed in Storage of derived
datasets, and dataset-level metadata is included in Derived dataset and pipeline description.

### Metadata conventions

- Unlessspecifiedotherwise,individualsidecarJSONfilesandallmetadatafieldswithinareOPTIONAL.However,theappropriateuseofthesefilesandpertinentfields
    is very valuable and thus encouraged. Moreover, for some types of files, there may be one or more required metadata fields, in which case at least one metadata file
    containing that field must be located somewhere within the file’s hierarchy (per the Inheritance Principle).
- When chaining derivative pipelines, any JSON fields that were specified as mandatory in the input files SHOULD be propagated forward in the output file’s JSON
    provided they remain valid. Non-required JSON fields MAY be propagated, and are highly useful, but it is the pipeline’s responsibility to ensure that the values are
    still relevant and appropriate to the type of output data.

### File naming conventions.

- Filenames that are permissible for a raw BIDS data type have a privileged status. Any modification of raw files must use a modified filename that does not conflict
    with the raw filename. Further, any files created as part of a derivative dataset must not match a permissible filename of a valid raw dataset. Stated equivalently,
    if any filename in a derivative dataset has a name permissible for a raw BIDS data, then that file must be an identical copy of that raw file.
- Each Derivatives filename MUST be of the form: <source_entities>[_keyword-<value>]_<suffix>.<ext>(where<value>could either be an<index>or a
    <label>depending on the keyword; see Definitions)
- Whenthederivativeschaininvolvesoutputsderivedfromasinglerawinput,source_entitiesMUSTbetheentiresourcefilename,withtheomissionofthesource
    suffix and extension. One exception to this rule is filename entities that are no longer relevant. Depending on the nature of the derivative file, the suffix can either
    be the same as the source file if that suffix is still appropriate, or a new appropriate value selected from the controlled list.


- There is no prohibition against identical filenames in different derived datasets, although users should be aware of the potential ambiguity this can create and use
    the sidecar JSON files to detail the specifics of individual files.
- When necessary to distinguish two files that do not otherwise have a distinguishing entity, the_desc-<label>entity SHOULD be used. This includes the cases of
    needing to distinguish both differing inputs and differing outputs (for example,_desc-T1wand_desc-T2wto distinguish brain mask files derived from T1w and
    T2w images; or_desc-sm4and_desc-sm8to distinguish between outputs generated with two different levels of smoothing).
- Whennamingfilesthatarenotyetstandardized,itisRECOMMENDEDtousenamesconsistentwithBIDSconventionswherethoseconventionsapply. Forexample,
    if a summary statistic is derived from a given task, the file name SHOULD contain_task-<label>.


## Common data types and metadata

### Common file level metadata fields

Each derivative data file SHOULD be described by a JSON file provided as a sidecar or higher up in the hierarchy of the derived dataset (according to the Inheritance
Principle) unless a particular derivative includes REQUIRED metadata fields, in which case a JSON file is also REQUIRED. Each derivative type defines their own set of
fields, but all of them share the following (non-required) ones:

Key name Requirement Level Data type Description

Description RECOMMENDED string Free-form natural language description.
This describes the nature of the file.
Sources OPTIONAL arrayofstrings A list of files with the paths specified
using Sources; these files were directly
used in the creation of this derivative
data file. For example, if a derivative A
is used in the creation of another
derivative B, which is in turn used to
generate C in a chain of A->B->C, C
should only list B in"Sources", and B
should only list A in"Sources".
However, in case both X and Y are
directly used in the creation of Z, then Z
should list X and Y in"Sources",
regardless of whether X was used to
generate Y. Using paths specified
relative to the dataset root is Sources.


Key name Requirement Level Data type Description

RawSources RawSources arrayofstrings A list of paths relative to dataset root
pointing to the BIDS-Raw file(s) that
were used in the creation of this
derivative. This field is DEPRECATED,
and this metadata SHOULD be recorded
in theSourcesfield using RawSources
to distinguish sources from different
datasets.

#### Examples

PreprocessedboldNIfTI file in the original coordinate space of the original run. The location of the file in the original datasets is encoded in theSourcesmetadata, and
_desc-<label>is used to prevent clashing with the original filename.

```
sub-01/
func/
sub-01_task-rest_desc-preproc_bold.nii.gz
sub-01_task-rest_desc-preproc_bold.json
```
{
"Sources":["bids:raw:sub-01/func/sub-01_task-rest_bold.nii.gz"]
}

Note that"raw"must appear in theDatasetLinksmetadata indataset_description.json. For example, in the case that the given derivatives dataset is nested within
the ”derivatives” directory of a raw dataset, the entry inDatasetLinksmay say:"raw": "../..".

If this file was generated with prior knowledge from additional sources, such as the same subject’sT1w, then both files MAY be included inSources.

{
"Sources":[
"bids:raw:sub-01/func/sub-01_task-rest_bold.nii.gz",
"bids:raw:sub-01/anat/sub-01_T1w.nii.gz"
]
}

On the other hand, if a preprocessed version of the T1w image was used, and it also occurs in the derivatives,Sourcesmay include both the local, derivative file, and the
raw original file.

{
"Sources":[
"bids::sub-01/anat/sub-01_desc-preproc_T1w.nii.gz"
"bids:raw:sub-01/func/sub-01_task-rest_bold.nii.gz"


##### ],

##### }

### Spatial references.

Derivatives are often aligned to a common spatial reference to allow for the comparison of acquired data across runs, sessions, subjects or datasets. A file may indicate
the spatial reference to which it has been aligned using thespaceentity and/or theSpatialReferencemetadata.

Thespaceentity may take any value in Image-Based Coordinate Systems.

If thespaceentity is omitted, or the space is not in the Standard template identifiers table, then theSpatialReferencemetadata is REQUIRED.

Key name Requirement Level Data type Description

SpatialReference RECOMMENDED if the derivative is
aligned to a standard template listed in
Standard template identifiers.
REQUIRED otherwise.

```
stringorobject For images with a single reference, the
value MUST be a single string. For
images with multiple references, such as
surface and volume references, a JSON
object MUST be used.
```
#### SpatialReference key allowed values

Value Description

"orig" A (potentially unique) per-image space. Useful for describing the source of
transforms from an input image to a target space.
[URI][] This can be used to point to a specific file. Paths written relative to the root of the
derivative dataset are [DEPRECATED][] in favor of [BIDS URIs][].

In the case of images with multiple references, anobjectmust link the relevant structures to reference files. If a single volumetric reference is used for multiple structures,
theVolumeReferencekey MAY be used to reduce duplication. For CIFTI-2 images, the relevant structures are BrainStructure values defined in the BrainModel elements
found in the CIFTI-2 header.

#### Examples

PreprocessedboldNIfTI file inindividualcoordinate space. Please mind that in this caseSpatialReferencekey is REQUIRED.

```
sub-01/
func/
sub-01_task-rest_space-individual_bold.nii.gz
sub-01_task-rest_space-individual_bold.json
```

##### {

"SpatialReference": "bids::sub-01/anat/sub-01_desc-combined_T1w.nii.gz"
}

PreprocessedboldCIFTI-2 files that have been sampled to the fsLR surface meshes defined in the Conte69 atlas along with the MNI152NLin6Asym template. In this
example, because all volumetric structures are sampled to the same reference, theVolumeReferencekey is used as a default, and only the surface references need to be
specified by BrainStructure names. Here referred to via ”https” [URIs][].

```
sub-01/
func/
sub-01_task-rest_space-fsLR_den-91k_bold.dtseries.nii
sub-01_task-rest_space-fsLR_den-91k_bold.json
```
{
"SpatialReference": {
"VolumeReference":"https://templateflow.s3.amazonaws.com/tpl-MNI152NLin6Asym_res-02_T1w.nii.gz",
"CIFTI_STRUCTURE_CORTEX_LEFT":"https://github.com/mgxd/brainplot/raw/master/brainplot/Conte69_Atlas/Conte69.L.midthickness.32k_fs_LR.surf.gii",
"CIFTI_STRUCTURE_CORTEX_RIGHT":"https://github.com/mgxd/brainplot/raw/master/brainplot/Conte69_Atlas/Conte69.R.midthickness.32k_fs_LR.surf.gii"
}
}

### Preprocessed or cleaned data

Template:

<pipeline_name>/
sub-<label>/
<datatype>/
<source_entities>[_space-<space>][_desc-<label>]_<suffix>.<ext>

Dataisconsideredtobepreprocessedorcleanedifthedatatypeoftheinput,asexpressedbytheBIDSsuffix,isunchanged. Bycontrast,processingstepsthatchangethe
number of dimensions are likely to disrupt the propagation of the input’ssuffixand generally, the outcomes of such transformation cannot be considered preprocessed
or cleaned data.

Examples of preprocessing:

- Motion-corrected, temporally denoised, and transformed to MNI space BOLD series
- Inhomogeneity corrected and skull stripped T1w files
- Motion-corrected DWI files
- Time-domain filtered EEG data
- MaxFilter (for example, SSS) cleaned MEG data

Thespaceentity is recommended to distinguish files with different underlying coordinate systems or registered to different reference maps. See Spatial references for
details. Thedescentity (”description”) is a general purpose field with freeform values, which SHOULD be used to distinguish between multiple different versions of


processing for the same input data.

Examples of preprocessed data:

```
pipeline1/
sub-001/
anat/
sub-001_space-MNI305_T1w.nii.gz
sub-001_space-MNI305_T1w.json
func/
sub-001_task-rest_run-1_space-MNI305_desc-preproc_bold.nii.gz
sub-001_task-rest_run-1_space-MNI305_desc-preproc_bold.json
pipeline2/
sub-001/
eeg/
sub-001_task-listening_run-1_desc-autoannotation_events.tsv
sub-001_task-listening_run-1_desc-autoannotation_events.json
sub-001_task-listening_run-1_desc-filtered_eeg.edf
sub-001_task-listening_run-1_desc-filtered_eeg.json
```
All REQUIRED metadata fields coming from a derivative file’s source file(s) MUST be propagated to the JSON description of the derivative unless the processing makes
them invalid (for example, if a source 4D image is averaged to create a single static volume, aRepetitionTimeproperty would no longer be relevant).


## Imaging data types

```
This section pertains to imaging data, which characteristically have spatial extent and resolution.
```
### Preprocessed, coregistered and/or resampled volumes.

```
Template:
<pipeline_name>/
sub-<label>/
<datatype>/
<source_entities>[_space-<space>][_res-<label>][_den-<label>][_desc-<label>]_<suffix>.<ext>
Volumetric preprocessing does not modify the number of dimensions, and so the specifications in Preprocessed or cleaned data apply. The use of surface meshes and
volumetric measures sampled to those meshes is sufficiently similar in practice to treat them equivalently.
```
When two or more instances of a given derivative are provided with resolution or surface sampling density being the only difference between them, then theres(for
resolution of regularly sampled N-D data) and/orden(for density of non-parametric surfaces) entities SHOULD be used to avoid name conflicts. Note that only files
combining both regularly sampled (for example, gridded) and surface sampled data (and their downstream derivatives) are allowed to present bothresanddenentities
simultaneously.
Examples:
pipeline1/
sub-001/
func/
sub-001_task-rest_run-1_space-MNI305_res-lo_bold.nii.gz
sub-001_task-rest_run-1_space-MNI305_res-hi_bold.nii.gz
sub-001_task-rest_run-1_space-MNI305_bold.json
The following metadata JSON fields are defined for preprocessed images:


Key name Requirement Level Data type Description

SkullStripped REQUIRED boolean Whether the volume was skull stripped
(non-brain voxels set to zero) or not.
Must be one of:"true","false".
Resolution REQUIRED ifresis present stringorobjectofstrings Specifies the interpretation of the
resolution keyword. If an object is used,
then the keys should be values for the
resentity and values should be
descriptions of thoseresvalues.
Density REQUIRED ifdenis present stringorobjectofstrings Specifies the interpretation of the
density keyword. If an object is used,
then the keys should be values for the
denentity and values should be
descriptions of thosedenvalues.

Example JSON file corresponding topipeline1/sub-001/func/sub-001_task-rest_run-1_space-MNI305_bold.jsonabove:

{
"SkullStripped": **true** ,
"Resolution": {
"hi":"Matched with high-resolution T1w (0.7mm, isotropic)",
"lo":"Matched with original BOLD resolution (2x2x3 mm^3)"
}
}

ThiswouldbeequivalenttohavingtwoJSONmetadatafiles,onecorrespondingtores-lo(pipeline1/sub-001/func/sub-001_task-rest_run-1_space-MNI305_res-lo_bold.json):

{
"SkullStripped": **true** ,
"Resolution": "Matched with original BOLD resolution (2x2x3 mm^3)"
}

And one corresponding tores-hi(pipeline1/sub-001/func/sub-001_task-rest_run-1_space-MNI305_res-hi_bold.json):

{
"SkullStripped": **true** ,
"Resolution": "Matched with high-resolution T1w (0.7mm, isotropic)"
}

Example of CIFTI-2 files (a format that combines regularly sampled data and non-parametric surfaces) having bothresanddenentities:

```
pipeline1/
```

```
sub-001/
func/
sub-001_task-rest_run-1_space-fsLR_res-1_den-10k_bold.dtseries.nii
sub-001_task-rest_run-1_space-fsLR_res-1_den-41k_bold.dtseries.nii
sub-001_task-rest_run-1_space-fsLR_res-2_den-10k_bold.dtseries.nii
sub-001_task-rest_run-1_space-fsLR_res-2_den-41k_bold.dtseries.nii
sub-001_task-rest_run-1_space-fsLR_bold.json
```
And the correspondingsub-001_task-rest_run-1_space-fsLR_bold.jsonfile:

{
"SkullStripped": **true** ,
"Resolution":{
"1":"Matched with MNI152NLin6Asym 1.6mm isotropic",
"2":"Matched with MNI152NLin6Asym 2.0mm isotropic"
},
"Density":{
"10k":"10242 vertices per hemisphere (5th order icosahedron)",
"41k":"40962 vertices per hemisphere (6th order icosahedron)"
}
}

### Masks

Template:

<pipeline_name>/
sub-<label>/
anat|func|dwi/
<source_entities>[_space-<space>][_res-<label>][_den-<label>][_label-<label>][_desc-<label>]_mask.nii.gz

A binary (1 - inside, 0 - outside) mask in the space defined by thespaceentity. If no transformation has taken place, the value ofspaceSHOULD be set toorig. If the
mask is an ROI mask derived from an atlas, then thelabelentity) SHOULD be used to specify the masked structure (see Common image-derived labels), and theAtlas
metadata SHOULD be defined.

JSON metadata fields:


Key name Requirement Level Data type Description

Type RECOMMENDED string Short identifier of the mask. The value
"Brain"refers to a brain mask. The
value"Lesion"refers to a lesion mask.
The value"Face"refers to a face mask.
The value"ROI"refers to a region of
interest mask. Must be one of:"Brain",
"Lesion","Face","ROI".
Sources RECOMMENDED arrayofstrings A list of files with the paths specified
using Sources; these files were directly
used in the creation of this derivative
data file. For example, if a derivative A
is used in the creation of another
derivative B, which is in turn used to
generate C in a chain of A->B->C, C
should only list B in"Sources", and B
should only list A in"Sources".
However, in case both X and Y are
directly used in the creation of Z, then Z
should list X and Y in"Sources",
regardless of whether X was used to
generate Y. Using paths specified
relative to the dataset root is Sources.
RawSources RawSources arrayofstrings A list of paths relative to dataset root
pointing to the BIDS-Raw file(s) that
were used in the creation of this
derivative. This field is DEPRECATED,
and this metadata SHOULD be recorded
in theSourcesfield using RawSources
to distinguish sources from different
datasets.
Atlas RECOMMENDED iflabelentity is
defined

string Which atlas (if any) was used to
generate the mask.
Resolution REQUIRED ifresis present stringorobjectofstrings Specifies the interpretation of the
resolution keyword. If an object is used,
then the keys should be values for the
resentity and values should be
descriptions of thoseresvalues.


Key name Requirement Level Data type Description

Density REQUIRED ifdenis present stringorobjectofstrings Specifies the interpretation of the
density keyword. If an object is used,
then the keys should be values for the
denentity and values should be
descriptions of thosedenvalues.

Examples:

```
func_loc/
sub-001/
func/
sub-001_task-rest_run-1_space-MNI305_desc-PFC_mask.nii.gz
sub-001_task-rest_run-1_space-MNI305_desc-PFC_mask.json
manual_masks/
sub-001/
anat/
sub-001_desc-tumor_mask.nii.gz
sub-001_desc-tumor_mask.json
```
### Segmentations

A segmentation is a labeling of regions of an image such that each location (for example, a voxel or a surface vertex) is identified with a label or a combination of labels.
Labeled regions may include anatomical structures (such as tissue class, Brodmann area or white matter tract), discontiguous, functionally-defined networks, tumors or
lesions.

A discrete segmentation represents each region with a unique integer label. A probabilistic segmentation represents each region as values between 0 and 1 (inclusive) at
each location in the image, and one volume/frame per structure may be concatenated in a single file.

Segmentations may be defined in a volume (labeled voxels), a surface (labeled vertices) or a combined volume/surface space.

If the segmentation can be derived from different atlases, theatlasentity MAY be used to distinguish the different segmentations. If so, theAtlasmetadata SHOULD
also be defined.

Thefollowingsectiondescribesdiscreteandprobabilisticsegmentationsofvolumes,followedbydiscretesegmentationsofsurface/combinedspaces. Probabilisticsegmen-
tations of surfaces are currently [unspecified][].

The following metadata fields apply to all segmentation files:


Key name Requirement Level Data type Description

Manual OPTIONAL boolean Indicates if the segmentation was
performed manually or via an
automated process. Must be one of:
"true","false".
Atlas RECOMMENDED ifatlasis present string Which atlas (if any) was used to
generate the mask.
Resolution REQUIRED ifresis present stringorobjectofstrings Specifies the interpretation of the
resolution keyword. If an object is used,
then the keys should be values for the
resentity and values should be
descriptions of thoseresvalues.
Density REQUIRED ifdenis present stringorobjectofstrings Specifies the interpretation of the
density keyword. If an object is used,
then the keys should be values for the
denentity and values should be
descriptions of thosedenvalues.

#### Discrete Segmentations

Discrete segmentations of brain tissue represent multiple anatomical structures (such as tissue class or Brodmann area) with a unique integer label in a 3D volume. See
Common image-derived labels for a description of how integer values map to anatomical structures.

Template:

<pipeline_name>/
sub-<label>/
anat|func|dwi/
<source_entities>[_space-<space>][_atlas-<label>][_res-<label>][_den-<label>]_dseg.nii.gz

Example:

```
pipeline/
sub-001/
anat/
sub-001_space-orig_dseg.nii.gz
sub-001_space-orig_dseg.json
```
A segmentation can be used to generate a binary mask that functions as a discrete ”label” for a single structure. In this case, the mask suffix MUST be used, thelabel
entity) SHOULD be used to specify the masked structure (see Common image-derived labels), theatlasentity and theAtlasmetadata SHOULD be defined.

For example:


```
pipeline/
sub-001/
anat/
sub-001_space-orig_atlas-Desikan_label-GM_mask.nii.gz
sub-001_space-orig_atlas-Desikan_label-GM_mask.json
```
#### Probabilistic Segmentations.

Probabilistic segmentations of brain tissue represent a single anatomical structure with values ranging from 0 to 1 in individual 3D volumes or across multiple frames. If
a single structure is included, thelabelentity SHOULD be used to specify the structure.

Template:

<pipeline_name>/
sub-<label>/
func|anat|dwi/
<source_entities>[_space-<space>][_atlas-<label>][_res-<label>][_den-<label>][_label-<label>]_probseg.nii.gz

Example:

```
pipeline/
sub-001/
anat/
sub-001_space-orig_label-BG_probseg.nii.gz
sub-001_space-orig_label-WM_probseg.nii.gz
```
See Common image-derived labels for reserved values for thelabelentity.

A 4D probabilistic segmentation, in which each frame corresponds to a different tissue class, must provide a label mapping in its JSON sidecar. For example:

```
pipeline/
sub-001/
anat/
sub-001_space-orig_probseg.nii.gz
sub-001_space-orig_probseg.json
```
The JSON sidecar MUST include the label-map key that specifies a tissue label for each volume:

{
"LabelMap": [
"BG",
"WM",
"GM"
]
}


Values oflabelSHOULD correspond to abbreviations defined in Common image-derived labels.

#### Discrete surface segmentations

Discrete surface segmentations (sometimes called parcellations) of cortical structures MUST be stored as GIFTI label files, with the extension.label.gii. For combined
volume/surface spaces, discrete segmentations MUST be stored as CIFTI-2 dense label files, with the extension.dlabel.nii.

Template:

<pipeline_name>/
sub-<label>/
anat/
<source_entities>[_hemi-{L|R}][_space-<space>][_atlas-<label>][_res-<label>][_den-<label>]_dseg.{label.gii|dlabel.nii}

Thehemi-<label>entity is REQUIRED for GIFTI files storing information about a structure that is restricted to a hemibrain. For example:

```
pipeline/
sub-001/
anat/
sub-001_hemi-L_dseg.label.gii
sub-001_hemi-R_dseg.label.gii
```
The REQUIRED extension for CIFTI parcellations is.dlabel.nii. For example:

```
pipeline/
sub-001/
anat/
sub-001_dseg.dlabel.nii
```
#### Common image-derived labels

BIDS supplies a standard, generic label-index mapping, defined in the table below, that contains common image-derived segmentations and can be used to map segmen-
tations (and parcellations) between lookup tables.

```
Integer value Description Abbreviation (label)
0 Background BG
1 Gray Matter GM
2 White Matter WM
3 Cerebrospinal Fluid CSF
4 Bone B
5 Soft Tissue ST
6 Non-brain NB
7 Lesion L
```

```
Integer value Description Abbreviation (label)
8 Cortical Gray Matter CGM
9 Subcortical Gray Matter SGM
10 Brainstem BS
11 Cerebellum CBM
```
These definitions can be overridden (or added to) by providing custom labels in a sidecar<matches>.tsvfile, in which<matches>corresponds to segmentation filename.

Example:

```
pipeline/
sub-001/
anat/
sub-001_space-orig_dseg.nii.gz
sub-001_space-orig_dseg.tsv
```
Definitions can also be specified with a top-leveldseg.tsv, which propagates to segmentations in relative subdirectories.

Example:

```
pipeline/
dseg.tsv
sub-001/
anat/
sub-001_space-orig_dseg.nii.gz
```
These TSV lookup tables contain the following columns:

Column name Requirement Level Data type Description

index REQUIRED integer The label integer index. Values in
indexMUST be unique.
name REQUIRED string The unique label name.
abbreviation OPTIONAL string The unique label abbreviation
color OPTIONAL string Hexadecimal. Label color for
visualization.
mapping OPTIONAL integer Corresponding integer label in the
standard BIDS label lookup.
Additional Columns NOT ALLOWED n/a Additional columns are not allowed.

An example, customdseg.tsvthat defines three labels:


index name abbreviation color mapping
100 Gray Matter GM #ff53bb 1
101 White Matter WM #2f8bbe 2
102 Brainstem BS #36de72 11

The following exampledseg.tsvdefines regions that are not part of the standard BIDS labels:

index name abbreviation
137 pars opercularis IFGop
138 pars triangularis IFGtr
139 pars orbitalis IFGor


## Longitudinal and multi-site studies

Multiplesessions(visits)areencodedbyaddinganextralayerofdirectoriesandfilenamesintheformofasession(forexampleses-<label>)andwitha*_sessions.tsv
file.

```
sub-control01/
ses-predrug/
anat/
sub-control01_ses-predrug_T1w.nii.gz
sub-control01_ses-predrug_T1w.json
sub-control01_ses-predrug_T2w.nii.gz
sub-control01_ses-predrug_T2w.json
func/
sub-control01_ses-predrug_task-nback_bold.nii.gz
sub-control01_ses-predrug_task-nback_bold.json
sub-control01_ses-predrug_task-nback_events.tsv
sub-control01_ses-predrug_task-nback_physio.tsv.gz
sub-control01_ses-predrug_task-nback_physio.json
sub-control01_ses-predrug_task-nback_sbref.nii.gz
dwi/
sub-control01_ses-predrug_dwi.nii.gz
sub-control01_ses-predrug_dwi.bval
sub-control01_ses-predrug_dwi.bvec
fmap/
sub-control01_ses-predrug_phasediff.nii.gz
sub-control01_ses-predrug_phasediff.json
sub-control01_ses-predrug_magnitude1.nii.gz
sub-control01_ses-predrug_scans.tsv
ses-postdrug/
func/
sub-control01_ses-postdrug_task-nback_bold.nii.gz
```

```
sub-control01_ses-postdrug_task-nback_bold.json
sub-control01_ses-postdrug_task-nback_events.tsv
sub-control01_ses-postdrug_task-nback_physio.tsv.gz
sub-control01_ses-postdrug_task-nback_physio.json
sub-control01_ses-postdrug_task-nback_sbref.nii.gz
fmap/
sub-control01_ses-postdrug_phasediff.nii.gz
sub-control01_ses-postdrug_phasediff.json
sub-control01_ses-postdrug_magnitude1.nii.gz
participants.tsv
dataset_description.json
README
CHANGES
```
### Multi-site or multi-center studies.

This version of the BIDS specification does not explicitly cover studies with data coming from multiple sites or multiple centers (such extension is planned inBIDS2.0.
There are however ways to model your data without any loss in terms of metadata.

#### Option 1: Treat each site/center as a separate dataset.

The simplest way of dealing with multiple sites is to treat data from each site as a separate and independent BIDS dataset with a separate participants.tsv and other
metadata files. This way you can feed each dataset individually to BIDS Apps and everything should just work.

#### Option 2: Combining sites/centers into one dataset

Alternatively you can combine data from all sites into one dataset. To identify which site each subjects comes from you can add asitecolumn in theparticipants.tsv
file indicating the source site. This solution allows you to analyze all of the subjects together in one dataset. One caveat is that subjects from all sites will have to have
unique labels. To enforce that and improve readability you can use a subject label prefix identifying the site. For examplesub-NUY001,sub-MIT002,sub-MPG002and so
on. Remember that hyphens and underscores are not allowed in subject labels.


## Glossary of schema objects

This section compiles the object definitions in the schema.

### ACCELChannelCount (metadata)

Name: Accelerometer channel count

Type: Metadata

Description: Number of accelerometer channels.

Schema information:

minimum **:** 0
type **:** integer

### Acknowledgements (metadata)

Name: Acknowledgements

Type: Metadata

Description: Text acknowledging contributions of individuals or institutions beyond those listed in Authors or Funding.

Schema information:

type **:** string

### AcquisitionDuration (metadata)

Name: Acquisition Duration


Type: Metadata

Description: Duration (in seconds) of volume acquisition. Corresponds to DICOM Tag 0018, 9073Acquisition Duration. This field is mutually exclusive with
"RepetitionTime".

Schema information:

exclusiveMinimum **:** 0
type **:** number
unit **:** s

### AcquisitionMode (metadata)

Name: Acquisition Mode

Type: Metadata

Description: Type of acquisition of the PET data (for example,"list mode").

Schema information:

type **:** string

### AcquisitionVoxelSize (metadata)

Name: Acquisition Voxel Size

Type: Metadata

Description: An array of numbers with a length of 3, in millimeters. This parameter denotes the original acquisition voxel size, excluding any inter-slice gaps and before
any interpolation or resampling within reconstruction or image processing. Any point spread function effects, for example due to T2-blurring, that would decrease the
effective resolution are not considered here.

Schema information:

items **:**
exclusiveMinimum **:** 0
type **:** number
unit **:** mm
maxItems **:** 3
minItems **:** 3
type **:** array


### Anaesthesia (metadata)

Name: Anaesthesia

Type: Metadata

Description: Details of anaesthesia used, if any.

Schema information:

type **:** string

### AnalyticalApproach (metadata)

Name: Analytical Approach

Type: Metadata

Description: Methodologyormethodologiesusedtoanalysethe"GeneticLevel". ValuesMUSTbetakenfromthedatabaseofGenotypesandPhenotypes(dbGaP)under
/Study/Molecular Data Type (for example, SNP Genotypes (Array) or Methylation (CpG).

Schema information:

anyOf **:**

**-** type **:** string
**-** items **:**
    type **:** string
type **:** array

### AnatomicalLandmarkCoordinateSystem (metadata)

Name: Anatomical Landmark Coordinate System

Type: Metadata

Allowed values: CTF, ElektaNeuromag, 4DBti, KitYokogawa, ChietiItab, Other, CapTrak, EEGLAB, EEGLAB-HJ, Other, ICBM452AirSpace, ICBM452Warp5Space,
IXI549Space,fsaverage,fsaverageSym, fsLR,MNIColin27,MNI152Lin,MNI152NLin2009aSym,MNI152NLin2009bSym,MNI152NLin2009cSym,MNI152NLin2009aAsym,
MNI152NLin2009bAsym,MNI152NLin2009cAsym,MNI152NLin6Sym,MNI152NLin6ASym,MNI305,NIHPD,OASIS30AntsOASISAnts,OASIS30Atropos,Talairach,UNCInfant,
fsaverage3,fsaverage4,fsaverage5,fsaverage6,fsaveragesym,UNCInfant0V21,UNCInfant1V21,UNCInfant2V21,UNCInfant0V22,UNCInfant1V22,UNCInfant2V22,
UNCInfant0V23,UNCInfant1V23,UNCInfant2V23

Description: Defines the coordinate system for the anatomical landmarks. See the Coordinate Systems Appendix for a list of restricted keywords for coordinate systems.
If"Other", provide definition of the coordinate system in"AnatomicalLandmarkCoordinateSystemDescription".

Schema information:


type **:** string

### AnatomicalLandmarkCoordinateSystemDescription (metadata).

Name: Anatomical Landmark Coordinate System Description

Type: Metadata

Description: Free-form text description of the coordinate system. May also include a link to a documentation page or paper describing the system in greater detail.

Schema information:

type **:** string

### AnatomicalLandmarkCoordinateUnits (metadata)

Name: Anatomical Landmark Coordinate Units

Type: Metadata

Allowed values:m,mm,cm,n/a

Description: Units of the coordinates of"AnatomicalLandmarkCoordinateSystem".

Schema information:

type **:** string

### AnatomicalLandmarkCoordinates sense 1 (metadata)

Name: Anatomical Landmark Coordinates

Type: Metadata

Description: Key-value pairs of the labels and 3-D digitized locations of anatomical landmarks, interpreted following the"AnatomicalLandmarkCoordinateSystem"(for
example,{"NAS": [12.7,21.3,13.9], "LPA": [5.2,11.3,9.6], "RPA": [20.2,11.3,9.1]}. Each array MUST contain three numeric values corresponding to x, y,
and z axis of the coordinate system in that exact order.

Schema information:

additionalProperties **:**
items **:**
type **:** number
maxItems **:** 3
minItems **:** 3


type **:** array
type **:** object

### AnatomicalLandmarkCoordinates sense 2 (metadata)

Name: Anatomical Landmark Coordinates

Type: Metadata

Description: Key-value pairs of any number of additional anatomical landmarks and their coordinates in voxel units (where first voxel has index 0,0,0) relative to the as-
sociated anatomical MRI (for example,{"AC": [127,119,149], "PC": [128,93,141], "IH": [131,114,206]}, or{"NAS": [127,213,139], "LPA": [52,113,96],
"RPA": [202,113,91]}). Each array MUST contain three numeric values corresponding to x, y, and z axis of the coordinate system in that exact order.

Schema information:

additionalProperties **:**
items **:**
type **:** number
maxItems **:** 3
minItems **:** 3
type **:** array
type **:** object

### Any (extensions)

Name: Any Extension

Type: Extension

Format:<entities>_<suffix>.*

Description: Any extension is allowed.

### ArterialSpinLabelingType (metadata)

Name: Arterial Spin Labeling Type

Type: Metadata

Allowed values:CASL,PCASL,PASL

Description: The arterial spin labeling type.

Schema information:


type **:** string

### AssociatedEmptyRoom (metadata).

Name: Associated Empty Room

Type: Metadata

Description: One or more BIDS URIs pointing to empty-room file(s) associated with the subject’s MEG recording. Using forward-slash separated paths relative to the
dataset root is BIDS URIs.

Schema information:

anyOf **:**

**-** items **:**
    anyOf **:**
    **-** format **:** dataset_relative
       type **:** string
    **-** format **:** bids_uri
       type **:** string
type **:** array
**-** format **:** dataset_relative
    type **:** string
**-** format **:** bids_uri
    type **:** string

### Atlas (metadata)

Name: Atlas

Type: Metadata

Description: Which atlas (if any) was used to generate the mask.

Schema information:

type **:** string

### AttenuationCorrection (metadata)

Name: Attenuation Correction

Type: Metadata


Description: Short description of the attenuation correction method used.

Schema information:

type **:** string

### AttenuationCorrectionMethodReference (metadata)

Name: Attenuation Correction Method Reference

Type: Metadata

Description: Reference paper for the attenuation correction method used.

Schema information:

type **:** string

### Authors (metadata)

Name: Authors

Type: Metadata

Description: List of individuals who contributed to the creation/curation of the dataset.

Schema information:

items **:**
type **:** string
type **:** array

### B0FieldIdentifier (metadata)

Name: B0 Field Identifier

Type: Metadata

Description: The presence of this key states that this particular 3D or 4D image MAY be used for fieldmap estimation purposes. Each"B0FieldIdentifier"MUST be a
unique string within one participant’s tree, shared only by the images meant to be used as inputs for the estimation of a particular instance of the B0 field estimation. It
is RECOMMENDED to derive this identifier from DICOM Tags, for example, DICOM tag 0018, 1030Protocol Name, or DICOM tag 0018, 0024Sequence Namewhen the
former is not defined (for example, in GE devices.)

Schema information:


anyOf **:**

**-** type **:** string
**-** items **:**
    type **:** string
type **:** array

### B0FieldSource (metadata)

Name: B0 Field Source

Type: Metadata

Description: At least one existing"B0FieldIdentifier"defined by images in the participant’s tree. This field states the B0 field estimation designated by the
"B0FieldIdentifier"that may be used to correct the dataset for distortions caused by B0 inhomogeneities."B0FieldSource"and"B0FieldIdentifier"MAY both
be present for images that are used to estimate their own B0 field, for example, in ”pepolar” acquisitions.

Schema information:

anyOf **:**

**-** type **:** string
**-** items **:**
    type **:** string
type **:** array

### BF (suffixes).

Name: Bright-field microscopy

Type: Suffix

Format:<entities>_BF.<extension>

Description: Bright-field microscopy imaging data

### BIDSVersion (metadata).

Name: BIDS Version

Type: Metadata

Description: The version of the BIDS standard that was used.

Schema information:


type **:** string

### BackgroundSuppression (metadata)

Name: Background Suppression

Type: Metadata

Description: Boolean indicating if background suppression is used.

Schema information:

type **:** boolean

### BackgroundSuppressionNumberPulses (metadata)

Name: Background Suppression Number Pulses

Type: Metadata

Description: The number of background suppression pulses used. Note that this excludes any effect of background suppression pulses applied before the labeling.

Schema information:

minimum **:** 0
type **:** number

### BackgroundSuppressionPulseTime (metadata)

Name: Background Suppression Pulse Time

Type: Metadata

Description: Array of numbers containing timing, in seconds, of the background suppression pulses with respect to the start of the labeling. In case of multi-PLD with
different background suppression pulse times, only the pulse time of the first PLD should be defined.

Schema information:

items **:**
minimum **:** 0
type **:** number
unit **:** s
type **:** array


### BasedOn (metadata).

Name: Based On

Type: Metadata

Description: List of files in a file collection to generate the map. Fieldmaps are also listed, if involved in the processing. This field is DEPRECATED, and this metadata
SHOULD be recorded in theSourcesfield using BIDS URIs to distinguish sources from different datasets.

Schema information:

anyOf **:**

**-** format **:** participant_relative
    type **:** string
**-** items **:**
    format **:** participant_relative
    type **:** string
    type **:** array

### BloodDensity (metadata)

Name: Blood Density

Type: Metadata

Description: Measured blood density. Unit of blood density should be in"g/mL".

Schema information:

type **:** number
unit **:** g/mL

### BodyPart (metadata)

Name: Body Part

Type: Metadata

Description: Body part of the organ / body region scanned.

Schema information:

type **:** string


### BodyPartDetails (metadata).

Name: Body Part Details

Type: Metadata

Description: Additional details about body part or location (for example:"corpus callosum").

Schema information:

type **:** string

### BodyPartDetailsOntology (metadata)

Name: Body Part Details Ontology

Type: Metadata

Description: URI of ontology used for BodyPartDetails (for example:"https://www.ebi.ac.uk/ols/ontologies/uberon").

Schema information:

format **:** uri
type **:** string

### BolusCutOffDelayTime (metadata).

Name: Bolus Cut Off Delay Time

Type: Metadata

Description: Duration between the end of the labeling and the start of the bolus cut-off saturation pulse(s), in seconds. This can be a number or array of numbers, of
which the values must be non-negative and monotonically increasing, depending on the number of bolus cut-off saturation pulses. For Q2TIPS, only the values for the
first and last bolus cut-off saturation pulses are provided. Based on DICOM Tag 0018, 925FASL Bolus Cut-off Delay Time.

Schema information:

anyOf **:**

**-** minimum **:** 0
    type **:** number
    unit **:** s
**-** items **:**
    minimum **:** 0
    type **:** number


```
unit : s
type : array
```
### BolusCutOffFlag (metadata)

Name: Bolus Cut Off Flag

Type: Metadata

Description: Boolean indicating if a bolus cut-off technique is used. Corresponds to DICOM Tag 0018, 925CASL Bolus Cut-off Flag.

Schema information:

type **:** boolean

### BolusCutOffTechnique (metadata)

Name: Bolus Cut Off Technique

Type: Metadata

Description: Name of the technique used, for example"Q2TIPS","QUIPSS","QUIPSSII". Corresponds to DICOM Tag 0018, 925EASL Bolus Cut-off Technique.

Schema information:

type **:** string

### BrainLocation (metadata)

Name: Brain Location

Type: Metadata

Description: Refers to the location in space of the"TissueOrigin". Values may be an MNI coordinate, a label taken from theAllen Brain Atlas, or layer to refer to
layer-specific gene expression, which can also tie up with laminar fMRI.

Schema information:

type **:** string

## CARS (suffixes).

Name: Coherent anti-Stokes Raman spectroscopy


Type: Suffix

Format:<entities>_CARS.<extension>

Description: Coherent anti-Stokes Raman spectroscopy imaging data

## CASLType (metadata).

Name: CASL Type

Type: Metadata

Allowed values:single-coil,double-coil

Description: Describes if a separate coil is used for labeling.

Schema information:

type **:** string

## CHANGES (files)

Name: Changelog

Type: Files And Directories

Description: Version history of the dataset (describing changes, updates and corrections) MAY be provided in the form of aCHANGEStext file. This file MUST follow the
CPAN Changelog convention. TheCHANGESfile MUST be either in ASCII or UTF-8 encoding.

Schema information:

file_type **:** regular

## CONF (suffixes).

Name: Confocal microscopy

Type: Suffix

Format:<entities>_CONF.<extension>

Description: Confocal microscopy imaging data


## CTF (extensions)

Name: CTF MEG Dataset Directory

Type: Extension

Format:<entities>_<suffix>.ds/

Description: A directory for MEG data, typically containing a.meg4file for the data and a.res4file for the resources.

## CapManufacturer (metadata).

Name: Cap Manufacturer

Type: Metadata

Description: Name of the cap manufacturer (for example,"EasyCap").

Schema information:

type **:** string

## CapManufacturersModelName (metadata)

Name: Cap Manufacturers Model Name

Type: Metadata

Description: Manufacturer’s designation of the cap model (for example,"actiCAP 64 Ch Standard-2").

Schema information:

type **:** string

## CellType (metadata).

Name: Cell Type

Type: Metadata

Description: Describes the type of cell analyzed. Values SHOULD come from thecell ontology.

Schema information:

type **:** string


## Chimap (suffixes).

Name: Quantitative susceptibility map (QSM)

Type: Suffix

Format:<entities>_Chimap.<extension>

Description: In parts per million (ppm). QSM allows for determining the underlying magnetic susceptibility of tissue (Chi) (Wang & Liu, 2014). Chi maps are REQUIRED
to use this suffix regardless of the method used to generate them.

Schema information:

unit **:** ppm

## ChunkTransformationMatrix (metadata)

Name: Chunk Transformation Matrix

Type: Metadata

Description: 3x3 or 4x4 affine transformation matrix describing spatial chunk transformation, for 2D and 3D respectively (for examples:[[2, 0, 0], [0, 3, 0], [0,
0, 1]]in 2D for 2x and 3x scaling along the first and second axis respectively; or[[1, 0, 0, 0], [0, 2, 0, 0], [0, 0, 3, 0], [0, 0, 0, 1]]in 3D for 2x and 3x
scaling along the second and third axis respectively). Note that non-spatial dimensions like time and channel are not included in the transformation matrix.

Schema information:

anyOf **:**

**-** items **:**
    items **:**
       type **:** number
    maxItems **:** 3
    minItems **:** 3
    type **:** array
maxItems **:** 3
minItems **:** 3
type **:** array
**-** items **:**
    items **:**
       type **:** number
    maxItems **:** 4
    minItems **:** 4
    type **:** array
maxItems **:** 4


```
minItems : 4
type : array
```
## ChunkTransformationMatrixAxis (metadata).

Name: Chunk Transformation Matrix Axis

Type: Metadata

Description: Describe the axis of the ChunkTransformationMatrix (for examples:["X", "Y"]or["Z", "Y", "X"]).

Schema information:

items **:**
type **:** string
maxItems **:** 3
minItems **:** 2
type **:** array

## Code (metadata)

Name: Code

Type: Metadata

Description: URI of the code used to present the stimuli. Persistent identifiers such as DOIs are preferred. If multiple versions of code may be hosted at the same location,
revision-specific URIs are recommended.

Schema information:

format **:** uri
type **:** string

## CogAtlasID (metadata)

Name: Cognitive Atlas ID

Type: Metadata

Description: URI of the correspondingCognitive AtlasTask term.

Schema information:

format **:** uri
type **:** string


## CogPOID (metadata).

Name: Cognitive Paradigm Ontology ID

Type: Metadata

Description: URI of the correspondingCogPOterm.

Schema information:

format **:** uri
type **:** string

## CoilCombinationMethod (metadata)

Name: Coil Combination Method

Type: Metadata

Description: AlmostallfMRIstudiesusingphased-arraycoilsuseroot-sum-of-squares(rSOS)combination,butothermethodsexist. Theimagereconstructionischanged
by the coil combination method (as for the matrix coil mode above), so anything non-standard should be reported.

Schema information:

type **:** string

## Columns (metadata).

Name: Columns

Type: Metadata

Description: Names of columns in file.

Schema information:

items **:**
type **:** string
type **:** array

## ContinuousHeadLocalization (metadata).

Name: Continuous Head Localization

Type: Metadata


Description:trueorfalsevalue indicating whether continuous head localisation was performed.

Schema information:

type **:** boolean

## ContrastBolusIngredient (metadata)

Name: Contrast Bolus Ingredient

Type: Metadata

Allowed values:IODINE,GADOLINIUM,CARBON DIOXIDE,BARIUM,XENON

Description: Active ingredient of agent. Corresponds to DICOM Tag 0018, 1048Contrast/Bolus Ingredient.

Schema information:

type **:** string

## DCOffsetCorrection (metadata).

Name: DC Offset Correction

Type: Metadata

Description: A description of the method (if any) used to correct for a DC offset. If the method used was subtracting the mean value for each channel, use ”mean”.

Schema information:

type **:** string

## DF (suffixes)

Name: Dark-field microscopy

Type: Suffix

Format:<entities>_DF.<extension>

Description: Dark-field microscopy imaging data


## DIC (suffixes)

Name: Differential interference contrast microscopy

Type: Suffix

Format:<entities>_DIC.<extension>

Description: Differential interference contrast microscopy imaging data

## DatasetDOI (metadata)

Name: DatasetDOI

Type: Metadata

Description: The Digital Object Identifier of the dataset (not the corresponding paper). DOIs SHOULD be expressed as a valid URI; bare DOIs such as10.0.2.3/dfjj.10
are URI.

Schema information:

format **:** uri
type **:** string

## DatasetLinks (metadata)

Name: Dataset Links

Type: Metadata

Description: Used to map a given<dataset-name>from a BIDS URI of the formbids:<dataset-name>:path/within/datasetto a local or remote location. The
<dataset-name>:""(an empty string) is a reserved keyword that MUST NOT be a key inDatasetLinks(example:bids::path/within/dataset).

Schema information:

additionalProperties **:**
format **:** uri
type **:** string
type **:** object

## DatasetType (metadata).

Name: Dataset Type

Type: Metadata


Allowed values:raw,derivative

Description: The interpretation of the dataset. For backwards compatibility, the default value is"raw".

Schema information:

type **:** string

## DecayCorrectionFactor (metadata).

Name: Decay Correction Factor

Type: Metadata

Description: Decay correction factor for each frame.

Schema information:

items **:**
type **:** number
type **:** array

## DelayAfterTrigger (metadata)

Name: Delay After Trigger

Type: Metadata

Description: Duration (in seconds) from trigger delivery to scan onset. This delay is commonly caused by adjustments and loading times. This specification is entirely
independent of"NumberOfVolumesDiscardedByScanner"or"NumberOfVolumesDiscardedByUser", as the delay precedes the acquisition.

Schema information:

type **:** number
unit **:** s

## DelayTime (metadata).

Name: Delay Time

Type: Metadata

Description: Userspecifiedtime(inseconds)todelaytheacquisitionofdataforthefollowingvolume. Ifthefieldisnotpresentitisassumedtobesettozero. Corresponds
to Siemens CSA header fieldlDelayTimeInTR. This field is REQUIRED for sparse sequences using the"RepetitionTime"field that do not have the"SliceTiming"field
set to allowed for accurate calculation of ”acquisition time”. This field is mutually exclusive with"VolumeTiming".


Schema information:

type **:** number
unit **:** s

## Density (metadata).

Name: Density

Type: Metadata

Description: Specifies the interpretation of the density keyword. If an object is used, then the keys should be values for thedenentity and values should be descriptions
of thosedenvalues.

Schema information:

anyOf **:**

**-** type **:** string
**-** additionalProperties **:**
    type **:** string
type **:** object

## Derivative (metadata)

Name: Derivative

Type: Metadata

Description: Indicates that values in the corresponding column are transformations of values from other columns (for example a summary score based on a subset of
items in a questionnaire).

Schema information:

type **:** boolean

## Description (metadata)

Name: Description

Type: Metadata

Description: Free-form natural language description.

Schema information:


type **:** string

## DetectorType (metadata)

Name: Detector Type

Type: Metadata

Description: Type of detector. This is a free form description with the following suggested terms:"SiPD","APD". Preferably a specific model/part number is supplied. If
individual channels have differentDetectorType, then the field here should be specified as"mixed"and this column should be included inoptodes.tsv.

Schema information:

anyOf **:**

**-** format **:** unit
    type **:** string
**-** enum **:**
    **-** mixed
    type **:** string

## DeviceSerialNumber (metadata)

Name: Device Serial Number

Type: Metadata

Description: The serial number of the equipment that produced the measurements. A pseudonym can also be used to prevent the equipment from being identifiable, so
long as each pseudonym is unique within the dataset.

Schema information:

type **:** string

## DewarPosition (metadata).

Name: Dewar Position

Type: Metadata

Description: Position of the dewar during the MEG scan: "upright","supine"or"degrees"of angle from vertical: for example on CTF systems,"upright=15°,
supine=90°".

Schema information:


type **:** string

## DigitizedHeadPoints sense 1 (metadata)

Name: Digitized Head Points

Type: Metadata

Description:trueorfalsevalue indicating whether head points outlining the scalp/face surface are contained within this recording.

Schema information:

type **:** boolean

## DigitizedHeadPoints sense 2 (metadata)

Name: Digitized Head Points

Type: Metadata

Description: Relative path to the file containing the locations of digitized head points collected during the session (for example,"sub-01_headshape.pos"). RECOM-
MENDED for all MEG systems, especially for CTF and BTi/4D. For Elekta/Neuromag the head points will be stored in the fif file.

Schema information:

format **:** file_relative
type **:** string

## DigitizedHeadPointsCoordinateSystem (metadata)

Name: Digitized Head Points Coordinate System

Type: Metadata

Allowed values: CTF, ElektaNeuromag, 4DBti, KitYokogawa, ChietiItab, Other, CapTrak, EEGLAB, EEGLAB-HJ, Other, ICBM452AirSpace, ICBM452Warp5Space,
IXI549Space,fsaverage,fsaverageSym, fsLR,MNIColin27,MNI152Lin,MNI152NLin2009aSym,MNI152NLin2009bSym,MNI152NLin2009cSym,MNI152NLin2009aAsym,
MNI152NLin2009bAsym,MNI152NLin2009cAsym,MNI152NLin6Sym,MNI152NLin6ASym,MNI305,NIHPD,OASIS30AntsOASISAnts,OASIS30Atropos,Talairach,UNCInfant,
fsaverage3,fsaverage4,fsaverage5,fsaverage6,fsaveragesym,UNCInfant0V21,UNCInfant1V21,UNCInfant2V21,UNCInfant0V22,UNCInfant1V22,UNCInfant2V22,
UNCInfant0V23,UNCInfant1V23,UNCInfant2V23

Description: Defines the coordinate system for the digitized head points. See the Coordinate Systems Appendix for a list of restricted keywords for coordinate systems. If
"Other", provide definition of the coordinate system in"DigitizedHeadPointsCoordinateSystemDescription".

Schema information:


type **:** string

## DigitizedHeadPointsCoordinateSystemDescription (metadata).

Name: Digitized Head Points Coordinate System Description

Type: Metadata

Description: Free-form text description of the coordinate system. May also include a link to a documentation page or paper describing the system in greater detail.

Schema information:

type **:** string

## DigitizedHeadPointsCoordinateUnits (metadata)

Name: Digitized Head Points Coordinate Units

Type: Metadata

Allowed values:m,mm,cm,n/a

Description: Units of the coordinates of"DigitizedHeadPointsCoordinateSystem".

Schema information:

type **:** string

## DigitizedLandmarks (metadata)

Name: Digitized Landmarks

Type: Metadata

Description:trueorfalsevalue indicating whether anatomical landmark points (fiducials) are contained within this recording.

Schema information:

type **:** boolean

## Directory (extensions)

Name: Directory

Type: Extension


Format:<entities>_<suffix>/

Description: A directory with no extension. Corresponds to BTi/4D data.

## DispersionConstant (metadata)

Name: Dispersion Constant

Type: Metadata

Description: External dispersion time constant resulting from tubing in default unit seconds.

Schema information:

type **:** number
unit **:** s

## DispersionCorrected (metadata)

Name: Dispersion Corrected

Type: Metadata

Description: Booleanflagspecifyingwhethertheblooddatahavebeendispersion-corrected. NOTE:notcustomaryformanualsamples, andhenceshouldbesettofalse.

Schema information:

type **:** boolean

## DoseCalibrationFactor (metadata)

Name: Dose Calibration Factor

Type: Metadata

Description: Multiplication factor used to transform raw data (in counts/sec) to meaningful unit (Bq/ml). Corresponds to DICOM Tag 0054, 1322Dose Calibration
Factor.

Schema information:

type **:** number


## DwellTime (metadata).

Name: Dwell Time

Type: Metadata

Description: Actual dwell time (in seconds) of the receiver per point in the readout direction, including any oversampling. For Siemens, this corresponds to DICOM field
0019, 1018 (in ns). This value is necessary for the optional readout distortion correction of anatomicals in the HCP Pipelines. It also usefully provides a handle on the
readout bandwidth, which isn’t captured in the other metadata tags. Not to be confused with"EffectiveEchoSpacing", and the frequent mislabeling of echo spacing
(which is spacing in the phase encoding direction) as ”dwell time” (which is spacing in the readout direction).

Schema information:

type **:** number
unit **:** s

## ECGChannelCount (metadata)

Name: ECG Channel Count

Type: Metadata

Description: Number of ECG channels.

Schema information:

minimum **:** 0
type **:** integer

## ECOGChannelCount (metadata)

Name: ECOG Channel Count

Type: Metadata

Description: Number of ECoG channels.

Schema information:

minimum **:** 0
type **:** integer

## EEGChannelCount (metadata)

Name: EEG Channel Count


Type: Metadata

Description: Number of EEG channels recorded simultaneously (for example, 21 ).

Schema information:

minimum **:** 0
type **:** integer

## EEGCoordinateSystem (metadata)

Name: EEG Coordinate System

Type: Metadata

Allowed values: CTF, ElektaNeuromag, 4DBti, KitYokogawa, ChietiItab, Other, CapTrak, EEGLAB, EEGLAB-HJ, Other, ICBM452AirSpace, ICBM452Warp5Space,
IXI549Space,fsaverage,fsaverageSym, fsLR,MNIColin27,MNI152Lin,MNI152NLin2009aSym,MNI152NLin2009bSym,MNI152NLin2009cSym,MNI152NLin2009aAsym,
MNI152NLin2009bAsym,MNI152NLin2009cAsym,MNI152NLin6Sym,MNI152NLin6ASym,MNI305,NIHPD,OASIS30AntsOASISAnts,OASIS30Atropos,Talairach,UNCInfant,
fsaverage3,fsaverage4,fsaverage5,fsaverage6,fsaveragesym,UNCInfant0V21,UNCInfant1V21,UNCInfant2V21,UNCInfant0V22,UNCInfant1V22,UNCInfant2V22,
UNCInfant0V23,UNCInfant1V23,UNCInfant2V23

Description: Defines the coordinate system for the EEG sensors.See the Coordinate Systems Appendix for a list of restricted keywords for coordinate systems. If"Other",
provide definition of the coordinate system inEEGCoordinateSystemDescription.

Schema information:

type **:** string

## EEGCoordinateSystemDescription (metadata)

Name: EEG Coordinate System Description

Type: Metadata

Description: Free-form text description of the coordinate system. May also include a link to a documentation page or paper describing the system in greater detail.

Schema information:

type **:** string

## EEGCoordinateUnits (metadata)

Name: EEG Coordinate Units

Type: Metadata


Allowed values:m,mm,cm,n/a

Description: Units of the coordinates ofEEGCoordinateSystem.

Schema information:

type **:** string

## EEGGround (metadata)

Name: EEG Ground

Type: Metadata

Description: Description of the location of the ground electrode (for example,"placed on right mastoid (M2)").

Schema information:

type **:** string

## EEGPlacementScheme (metadata)

Name: EEG Placement Scheme

Type: Metadata

Description: Placement scheme of EEG electrodes. Either the name of a standardized placement system (for example,"10-20") or a list of standardized electrode names
(for example,["Cz", "Pz"]).

Schema information:

type **:** string

## EEGReference (metadata).

Name: EEG Reference

Type: Metadata

Description: General description of the reference scheme used and (when applicable) of location of the reference electrode in the raw recordings (for example,"left
mastoid","Cz","CMS"). If different channels have a different reference, this field should have a general description and the channel specific reference should be defined
in thechannels.tsvfile.

Schema information:

type **:** string


## EMGChannelCount (metadata).

Name: EMG Channel Count

Type: Metadata

Description: Number of EMG channels.

Schema information:

minimum **:** 0
type **:** integer

## EOGChannelCount (metadata)

Name: EOG Channel Count

Type: Metadata

Description: Number of EOG channels.

Schema information:

minimum **:** 0
type **:** integer

## EchoTime sense 1 (metadata)

Name: Echo Time

Type: Metadata

Description: The echo time (TE) for the acquisition, specified in seconds. Corresponds to DICOM Tag 0018, 0081Echo Time(please note that the DICOM term is in
milliseconds not seconds). The data type number may apply to files from any MRI modality concerned with a single value for this field, or to the files in a file collection
where the value of this field is iterated using the file collection. The data type array provides a value for each volume in a 4D dataset and should only be used when the
volume timing is critical for interpretation of the data, such as in file collection or variable echo time fMRI sequences.

Schema information:

anyOf **:**

**-** exclusiveMinimum **:** 0
    type **:** number
    unit **:** s
**-** items **:**
    exclusiveMinimum **:** 0


```
type : number
unit : s
type : array
```
## EchoTime sense 2 (metadata)

Name: Echo Time

Type: Metadata

Description: The time (in seconds) when the echo corresponding to this map was acquired.

Schema information:

exclusiveMinimum **:** 0
type **:** number
unit **:** s

## EchoTime1 (metadata)

Name: Echo Time1

Type: Metadata

Description: The time (in seconds) when the first (shorter) echo occurs.

Schema information:

exclusiveMinimum **:** 0
type **:** number
unit **:** s

## EchoTime2 (metadata)

Name: Echo Time2

Type: Metadata

Description: The time (in seconds) when the second (longer) echo occurs.

Schema information:

exclusiveMinimum **:** 0
type **:** number
unit **:** s


## EffectiveEchoSpacing (metadata).

Name: Effective Echo Spacing

Type: Metadata

Description: The ”effective” sampling interval, specified in seconds, between lines in the phase-encoding direction, defined based on the size of the reconstructed image
in the phase direction. It is frequently, but incorrectly, referred to as ”dwell time” (see the"DwellTime"parameter for actual dwell time). It is required for unwarping
distortions using field maps. Note that beyond just in-plane acceleration, a variety of other manipulations to the phase encoding need to be accounted for properly,
including partial fourier, phase oversampling, phase resolution, phase field-of-view and interpolation.

Schema information:

exclusiveMinimum **:** 0
type **:** number
unit **:** s

## ElectricalStimulation (metadata).

Name: Electrical Stimulation

Type: Metadata

Description: Boolean field to specify if electrical stimulation was done during the recording (options aretrueorfalse). Parameters for event-like stimulation should be
specified in theevents.tsvfile.

Schema information:

type **:** boolean

## ElectricalStimulationParameters (metadata)

Name: Electrical Stimulation Parameters

Type: Metadata

Description: Free form description of stimulation parameters, such as frequency or shape. Specific onsets can be specified in the events.tsv file. Specific shapes can be
described here in freeform text.

Schema information:

type **:** string


## ElectrodeManufacturer (metadata).

Name: Electrode Manufacturer

Type: Metadata

Description: Can be used if all electrodes are of the same manufacturer (for example,"AD-TECH","DIXI"). If electrodes of different manufacturers are used, please use
the corresponding table in the_electrodes.tsvfile.

Schema information:

type **:** string

## ElectrodeManufacturersModelName (metadata)

Name: Electrode Manufacturers Model Name

Type: Metadata

Description: If different electrode types are used, please use the corresponding table in the_electrodes.tsvfile.

Schema information:

type **:** string

## EpochLength (metadata)

Name: Epoch Length

Type: Metadata

Description: Duration of individual epochs in seconds (for example, 1 ) in case of epoched data. If recording was continuous or discontinuous, leave out the field.

Schema information:

minimum **:** 0
type **:** number

## EstimationAlgorithm (metadata).

Name: Estimation Algorithm

Type: Metadata

Description: Type of algorithm used to perform fitting (for example,"linear","non-linear","LM"and such).


Schema information:

type **:** string

## EstimationReference (metadata)

Name: Estimation Reference

Type: Metadata

Description: Reference to the study/studies on which the implementation is based.

Schema information:

type **:** string

## EthicsApprovals (metadata).

Name: Ethics Approvals

Type: Metadata

Description: List of ethics committee approvals of the research protocols and/or protocol identifiers.

Schema information:

items **:**
type **:** string
type **:** array

## FLAIR (suffixes)

Name: Fluid attenuated inversion recovery image

Type: Suffix

Format:<entities>_FLAIR.<extension>

Description: Inarbitraryunits(arbitrary). StructuralimageswithpredominantT2contribution(alsoknownasT2-FLAIR),inwhichsignalfromfluids(forexample,CSF)
is nulled out by adjusting inversion time, coupled with notably long repetition and echo times.

Schema information:

unit **:** arbitrary


## FLASH (suffixes)

Name: Fast-Low-Angle-Shot image

Type: Suffix

Format:<entities>_FLASH.<extension>

Description: FLASH (Fast-Low-Angle-Shot) is a vendor-specific implementation for spoiled gradient echo acquisition. It is commonly used for rapid anatomical imaging
and also for many different qMRI applications. When used for a single file, it does not convey any information about the image contrast. When used in a file collection, it
may result in conflicts across filenames of different applications. Change: Removed from suffixes.

## FLUO (suffixes).

Name: Fluorescence microscopy

Type: Suffix

Format:<entities>_FLUO.<extension>

Description: Fluorescence microscopy imaging data

## FiducialsCoordinateSystem (metadata)

Name: Fiducials Coordinate System

Type: Metadata

Allowed values: CTF, ElektaNeuromag, 4DBti, KitYokogawa, ChietiItab, Other, CapTrak, EEGLAB, EEGLAB-HJ, Other, ICBM452AirSpace, ICBM452Warp5Space,
IXI549Space,fsaverage,fsaverageSym, fsLR,MNIColin27,MNI152Lin,MNI152NLin2009aSym,MNI152NLin2009bSym,MNI152NLin2009cSym,MNI152NLin2009aAsym,
MNI152NLin2009bAsym,MNI152NLin2009cAsym,MNI152NLin6Sym,MNI152NLin6ASym,MNI305,NIHPD,OASIS30AntsOASISAnts,OASIS30Atropos,Talairach,UNCInfant,
fsaverage3,fsaverage4,fsaverage5,fsaverage6,fsaveragesym,UNCInfant0V21,UNCInfant1V21,UNCInfant2V21,UNCInfant0V22,UNCInfant1V22,UNCInfant2V22,
UNCInfant0V23,UNCInfant1V23,UNCInfant2V23

Description: Defines the coordinate system for the fiducials. Preferably the same as the"EEGCoordinateSystem". See the Coordinate Systems Appendix for a list of
restricted keywords for coordinate systems. If"Other", provide definition of the coordinate system in"FiducialsCoordinateSystemDescription".

Schema information:

type **:** string

## FiducialsCoordinateSystemDescription (metadata)

Name: Fiducials Coordinate System Description


Type: Metadata

Description: Free-form text description of the coordinate system. May also include a link to a documentation page or paper describing the system in greater detail.

Schema information:

type **:** string

## FiducialsCoordinateUnits (metadata)

Name: Fiducials Coordinate Units

Type: Metadata

Allowed values:m,mm,cm,n/a

Description: Units in which the coordinates that are listed in the field"FiducialsCoordinateSystem"are represented.

Schema information:

type **:** string

## FiducialsCoordinates (metadata)

Name: Fiducials Coordinates

Type: Metadata

Description: Key-value pairs of the labels and 3-D digitized position of anatomical landmarks, interpreted following the"FiducialsCoordinateSystem"(for example,
{"NAS": [12.7,21.3,13.9], "LPA": [5.2,11.3,9.6], "RPA": [20.2,11.3,9.1]}). EacharrayMUSTcontainthreenumericvaluescorrespondingtox,y,andzaxis
of the coordinate system in that exact order.

Schema information:

additionalProperties **:**
items **:**
type **:** number
maxItems **:** 3
minItems **:** 3
type **:** array
type **:** object

## FiducialsDescription (metadata)

Name: Fiducials Description


Type: Metadata

Description: Free-formtextdescriptionofhowthefiducialssuchasvitamin-Ecapsuleswereplacedrelativetoanatomicallandmarks,andhowthepositionofthefiducials
were measured (for example,"both with Polhemus and with T1w MRI").

Schema information:

type **:** string

## FlipAngle (metadata)

Name: Flip Angle

Type: Metadata

Description: Flip angle (FA) for the acquisition, specified in degrees. Corresponds to: DICOM Tag 0018, 1314Flip Angle. The data type number may apply to files from
anyMRImodalityconcernedwithasinglevalueforthisfield,ortothefilesinafilecollectionwherethevalueofthisfieldisiteratedusingthefilecollection. Thedatatype
array provides a value for each volume in a 4D dataset and should only be used when the volume timing is critical for interpretation of the data, such as in file collection
or variable flip angle fMRI sequences.

Schema information:

anyOf **:**

**-** exclusiveMinimum **:** 0
    maximum **:** 360
    type **:** number
    unit **:** degree
**-** items **:**
    exclusiveMinimum **:** 0
    maximum **:** 360
    type **:** number
    unit **:** degree
    type **:** array

## FrameDuration (metadata)

Name: Frame Duration

Type: Metadata

Description: Time duration of each frame in default unit seconds. This corresponds to DICOM Tag 0018, 1242Actual Frame Durationconverted to seconds.

Schema information:


items **:**
type **:** number
type **:** array
unit **:** s

## FrameTimesStart (metadata)

Name: Frame Times Start

Type: Metadata

Description: Start times for all frames relative to"TimeZero"in default unit seconds.

Schema information:

items **:**
type **:** number
type **:** array
unit **:** s

## Funding (metadata)

Name: Funding

Type: Metadata

Description: List of sources of funding (grant numbers).

Schema information:

items **:**
type **:** string
type **:** array

## GYROChannelCount (metadata)

Name: Gyrometer Channel Count

Type: Metadata

Description: Number of gyrometer channels.

Schema information:


minimum **:** 0
type **:** integer

## GeneratedBy (metadata)

Name: Generated By

Type: Metadata

Description: Used to specify provenance of the dataset.

Schema information:

items **:**
properties **:**
CodeURL **:**
format **:** uri
type **:** string
Container **:**
properties **:**
Tag **:**
type **:** string
Type **:**
type **:** string
URI **:**
format **:** uri
type **:** string
type **:** object
Description **:**
type **:** string
Name **:**
type **:** string
Version **:**
type **:** string
type **:** object
minItems **:** 1
type **:** array

## GeneticLevel (metadata).

Name: Genetic Level


Type: Metadata

Description: Describes the level of analysis. Values MUST be one of"Genetic","Genomic","Epigenomic","Transcriptomic","Metabolomic", or"Proteomic".

Schema information:

anyOf **:**

**-** enum **:** &id001
    **-** Genetic
    **-** Genomic
    **-** Epigenomic
    **-** Transcriptomic
    **-** Metabolomic
    **-** Proteomic
    type **:** string
**-** items **:**
    enum **:** *id001
    type **:** string
    type **:** array

## Genetics (metadata)

Name: Genetics

Type: Metadata

Description: An object containing information about the genetics descriptor.

Schema information:

properties **:**
Database **:**
description **:** '[URI](../02-common-principles.md#uniform-resource-indicator)

```
of database where the dataset is hosted.
```
```
'
format : uri
name : Database
type : string
Dataset :
description : '[URI](../02-common-principles.md#uniform-resource-indicator)
```

```
where data can be retrieved.
```
```
'
format : uri
name : Dataset
type : string
Descriptors :
anyOf :
```
**-** type **:** string
**-** items **:**
    type **:** string
type **:** array
description **:** 'List of relevant descriptors (for example, journal articles) for
    dataset

```
using a valid
```
```
URI
```
```
when possible.
```
'
name **:** Descriptors
type **:** object

## GradientSetType (metadata)

Name: Gradient Set Type

Type: Metadata

Description: It should be possible to infer the gradient coil from the scanner model. If not, for example because of a custom upgrade or use of a gradient insert set, then
the specifications of the actual gradient coil should be reported independently.

Schema information:

type **:** string

## HED (columns)

Name: HED Tag


Type: Column

Description: Hierarchical Event Descriptor (HED) Tag. See the HED Appendix for details.

Schema information:

type **:** string

## HED (metadata)

Name: HED

Type: Metadata

Description: Hierarchical Event Descriptor (HED) information, see the HED Appendix for details.

Schema information:

anyOf **:**

**-** type **:** string
**-** additionalProperties **:**
    type **:** string
type **:** object

## HEDVersion (metadata)

Name: HED Version

Type: Metadata

Description: If HED tags are used: The version of the HED schema used to validate HED tags for study. May include a single schema or a base schema and one or more
library schema.

Schema information:

anyOf **:**

**-** format **:** hed_version
    type **:** string
**-** items **:**
    format **:** hed_version
    type **:** string
    type **:** array


## Haematocrit (metadata).

Name: Haematocrit

Type: Metadata

Description: Measured haematocrit, meaning the volume of erythrocytes divided by the volume of whole blood.

Schema information:

type **:** number

## HardcopyDeviceSoftwareVersion (metadata)

Name: Hardcopy Device Software Version

Type: Metadata

Description: Manufacturer’s designation of the software of the device that created this Hardcopy Image (the printer). Corresponds to DICOM Tag 0018, 101AHardcopy
Device Software Version.

Schema information:

type **:** string

## HardwareFilters (metadata).

Name: Hardware Filters

Type: Metadata

Description: Object of temporal hardware filters applied, or"n/a"if the data is not available. Each key-value pair in the JSON object is a name of the filter and
an object in which its parameters are defined as key-value pairs. For example,{"Highpass RC filter": {"Half amplitude cutoff (Hz)": 0.0159, "Roll-off":
"6dB/Octave"}}.

Schema information:

anyOf **:**

**-** additionalProperties **:**
    type **:** object
type **:** object
**-** enum **:**
    **-** n/a
    type **:** string


## HeadCircumference (metadata).

Name: Head Circumference

Type: Metadata

Description: Circumference of the participant’s head, expressed in cm (for example, 58 ).

Schema information:

exclusiveMinimum **:** 0
type **:** number
unit **:** cm

## HeadCoilCoordinateSystem (metadata)

Name: Head Coil Coordinate System

Type: Metadata

Allowed values: CTF, ElektaNeuromag, 4DBti, KitYokogawa, ChietiItab, Other, CapTrak, EEGLAB, EEGLAB-HJ, Other, ICBM452AirSpace, ICBM452Warp5Space,
IXI549Space,fsaverage,fsaverageSym, fsLR,MNIColin27,MNI152Lin,MNI152NLin2009aSym,MNI152NLin2009bSym,MNI152NLin2009cSym,MNI152NLin2009aAsym,
MNI152NLin2009bAsym,MNI152NLin2009cAsym,MNI152NLin6Sym,MNI152NLin6ASym,MNI305,NIHPD,OASIS30AntsOASISAnts,OASIS30Atropos,Talairach,UNCInfant,
fsaverage3,fsaverage4,fsaverage5,fsaverage6,fsaveragesym,UNCInfant0V21,UNCInfant1V21,UNCInfant2V21,UNCInfant0V22,UNCInfant1V22,UNCInfant2V22,
UNCInfant0V23,UNCInfant1V23,UNCInfant2V23

Description: Defines the coordinate system for the head coils. See the Coordinate Systems Appendix for a list of restricted keywords for coordinate systems. If"Other",
provide definition of the coordinate system inHeadCoilCoordinateSystemDescription.

Schema information:

type **:** string

## HeadCoilCoordinateSystemDescription (metadata)

Name: Head Coil Coordinate System Description

Type: Metadata

Description: Free-form text description of the coordinate system. May also include a link to a documentation page or paper describing the system in greater detail.

Schema information:

type **:** string


## HeadCoilCoordinateUnits (metadata)

Name: Head Coil Coordinate Units

Type: Metadata

Allowed values:m,mm,cm,n/a

Description: Units of the coordinates ofHeadCoilCoordinateSystem.

Schema information:

type **:** string

## HeadCoilCoordinates (metadata)

Name: Head Coil Coordinates

Type: Metadata

Description: Key-value pairs describing head localization coil labels and their coordinates, interpreted following theHeadCoilCoordinateSystem(for example,{"NAS":
[12.7,21.3,13.9], "LPA": [5.2,11.3,9.6], "RPA": [20.2,11.3,9.1]}). Notethatcoilsarenotalwaysplacedatlocationsthathaveaknownanatomicalname(for
example, for Elekta, Yokogawa systems); in that case generic labels can be used (for example,{"coil1": [12.2,21.3,12.3], "coil2": [6.7,12.3,8.6], "coil3":
[21.9,11.0,8.1]}). Each array MUST contain three numeric values corresponding to x, y, and z axis of the coordinate system in that exact order.

Schema information:

additionalProperties **:**
items **:**
type **:** number
maxItems **:** 3
minItems **:** 3
type **:** array
type **:** object

## HeadCoilFrequency (metadata).

Name: Head Coil Frequency

Type: Metadata

Description: List of frequencies (in Hz) used by the head localisation coils (’HLC’ in CTF systems, ’HPI’ in Elekta, ’COH’ in BTi/4D) that track the subject’s head position
in the MEG helmet (for example,[293, 307, 314, 321]).

Schema information:


anyOf **:**

**-** type **:** number
    unit **:** Hz
**-** items **:**
    type **:** number
    unit **:** Hz
    type **:** array

## HowToAcknowledge (metadata)

Name: How To Acknowledge

Type: Metadata

Description: Textcontaininginstructionsonhowresearchersusingthisdatasetshouldacknowledgetheoriginalauthors. Thisfieldcanalsobeusedtodefineapublication
that should be cited in publications that use the dataset.

Schema information:

type **:** string

## IRT1 (suffixes)

Name: Inversion recovery T1 mapping

Type: Suffix

Format:<entities>_IRT1.<extension>

Description: The IRT1 method involves multiple inversion recovery spin-echo images acquired at different inversion times (Barral et al. 2010).

## ImageAcquisitionProtocol (metadata)

Name: Image Acquisition Protocol

Type: Metadata

Description: Description of the image acquisition protocol or URI (for example fromprotocols.io).

Schema information:

type **:** string


## ImageDecayCorrected (metadata)

Name: Image Decay Corrected

Type: Metadata

Description: Boolean flag specifying whether the image data have been decay-corrected.

Schema information:

type **:** boolean

## ImageDecayCorrectionTime (metadata)

Name: Image Decay Correction Time

Type: Metadata

Description: Point in time from which the decay correction was applied with respect to"TimeZero"in the default unit seconds.

Schema information:

type **:** number
unit **:** s

## Immersion (metadata).

Name: Immersion

Type: Metadata

Description: Lens immersion medium. If the file format is OME-TIFF, the value MUST be consistent with theImmersionOME metadata field.

Schema information:

type **:** string

## InfusionRadioactivity (metadata)

Name: Infusion Radioactivity

Type: Metadata

Description: Amountofradioactivityinfusedintothepatient. Thisvaluemustbelessthanorequaltothetotalinjectedradioactivity("InjectedRadioactivity"). Units
should be the same as"InjectedRadioactivityUnits".


Schema information:

type **:** number

## InfusionSpeed (metadata)

Name: Infusion Speed

Type: Metadata

Description: If given, infusion speed.

Schema information:

type **:** number

## InfusionSpeedUnits (metadata)

Name: Infusion Speed Units

Type: Metadata

Description: Unit of infusion speed (for example,"mL/s").

Schema information:

format **:** unit
type **:** string

## InfusionStart (metadata)

Name: Infusion Start

Type: Metadata

Description: Time of start of infusion with respect to"TimeZero"in the default unit seconds.

Schema information:

type **:** number
unit **:** s


## InjectedMass (metadata).

Name: Injected Mass

Type: Metadata

Description: Total mass of radiolabeled compound injected into subject (for example, 10 ). This can be derived as the ratio of the"InjectedRadioactivity"and
"MolarRadioactivity". For those tracers in which injected mass is not available (for example FDG) can be set to **"n/a"** ).

Schema information:

anyOf **:**

**-** type **:** number
**-** enum **:**
    **-** n/a
    type **:** string

## InjectedMassPerWeight (metadata)

Name: Injected Mass Per Weight

Type: Metadata

Description: Injected mass per kilogram bodyweight.

Schema information:

type **:** number

## InjectedMassPerWeightUnits (metadata)

Name: Injected Mass Per Weight Units

Type: Metadata

Description: Unit format of the injected mass per kilogram bodyweight (for example,"ug/kg").

Schema information:

format **:** unit
type **:** string

## InjectedMassUnits (metadata).

Name: Injected Mass Units


Type: Metadata

Description: Unit format of the mass of compound injected (for example,"ug"or"umol"). Note this is not required for an FDG acquisition, since it is not available, and
SHOULD be set to **"n/a"**.

Schema information:

anyOf **:**

**-** format **:** unit
    type **:** string
**-** enum **:**
    **-** n/a
    type **:** string

## InjectedRadioactivity (metadata).

Name: Injected Radioactivity

Type: Metadata

Description: Total amount of radioactivity injected into the patient (for example, 400 ). For bolus-infusion experiments, this value should be the sum of all injected
radioactivity originating from both bolus and infusion. Corresponds to DICOM Tag 0018, 1074Radionuclide Total Dose.

Schema information:

type **:** number

## InjectedRadioactivityUnits (metadata).

Name: Injected Radioactivity Units

Type: Metadata

Description: Unit format of the specified injected radioactivity (for example,"MBq").

Schema information:

format **:** unit
type **:** string

## InjectedVolume (metadata).

Name: Injected Volume


Type: Metadata

Description: Injected volume of the radiotracer in the unit"mL".

Schema information:

type **:** number
unit **:** mL

## InjectionEnd (metadata).

Name: Injection End

Type: Metadata

Description: Time of end of injection with respect to"TimeZero"in the default unit seconds.

Schema information:

type **:** number
unit **:** s

## InjectionStart (metadata)

Name: Injection Start

Type: Metadata

Description: Time of start of injection with respect to"TimeZero"in the default unit seconds. This corresponds to DICOM Tag 0018, 1072Contrast/Bolus Start Time
converted to seconds relative to"TimeZero".

Schema information:

type **:** number
unit **:** s

## InstitutionAddress (metadata)

Name: Institution Address

Type: Metadata

Description: The address of the institution in charge of the equipment that produced the measurements.

Schema information:


type **:** string

## InstitutionName (metadata).

Name: Institution Name

Type: Metadata

Description: The name of the institution in charge of the equipment that produced the measurements.

Schema information:

type **:** string

## InstitutionalDepartmentName (metadata).

Name: Institutional Department Name

Type: Metadata

Description: The department in the institution in charge of the equipment that produced the measurements.

Schema information:

type **:** string

## Instructions (metadata)

Name: Instructions

Type: Metadata

Description: Text of the instructions given to participants before the recording.

Schema information:

type **:** string

## IntendedFor sense 1 (metadata).

Name: Intended For

Type: Metadata


Description: The paths to files for which the associated file is intended to be used. Contains one or more BIDS URIs. Using forward-slash separated paths relative to the
participant subdirectory is BIDS URIs.

Schema information:

anyOf **:**

**-** format **:** bids_uri
    type **:** string
**-** format **:** participant_relative
    type **:** string
**-** items **:**
    anyOf **:**
    **-** format **:** bids_uri
       type **:** string
    **-** format **:** participant_relative
       type **:** string
    type **:** array

## IntendedFor sense 2 (metadata).

Name: Intended For

Type: Metadata

Description: The paths to files for which the associated file is intended to be used. Contains one or more BIDS URIs. Using forward-slash separated paths relative to the
dataset root is BIDS URIs.

Schema information:

anyOf **:**

**-** format **:** bids_uri
    type **:** string
**-** format **:** dataset_relative
    type **:** string
**-** items **:**
    anyOf **:**
    **-** format **:** bids_uri
       type **:** string
    **-** format **:** dataset_relative
       type **:** string
    type **:** array


## InversionTime (metadata).

Name: Inversion Time

Type: Metadata

Description: The inversion time (TI) for the acquisition, specified in seconds. Inversion time is the time after the middle of inverting RF pulse to middle of excitation
pulse to detect the amount of longitudinal magnetization. Corresponds to DICOM Tag 0018, 0082Inversion Time(please note that the DICOM term is in milliseconds
not seconds).

Schema information:

exclusiveMinimum **:** 0
type **:** number
unit **:** s

## LICENSE (files).

Name: License

Type: Files And Directories

Description: ALICENSEfileMAYbeprovidedinadditiontotheshortspecificationoftheusedlicenseinthedataset_description.json "License"field. The"License"
field andLICENSEfile MUST correspond. TheLICENSEfile MUST be either in ASCII or UTF-8 encoding.

Schema information:

file_type **:** regular

## LabelingDistance (metadata)

Name: Labeling Distance

Type: Metadata

Description: Distancefromthecenteroftheimagingslabtothecenterofthelabelingplane((P)CASL)ortheleadingedgeofthelabelingslab(PASL),inmillimeters. Ifthe
labeling is performed inferior to the isocenter, this number should be negative. Based on DICOM macro C.8.13.5.14.

Schema information:

type **:** number
unit **:** mm


## LabelingDuration (metadata)

Name: Labeling Duration

Type: Metadata

Description: Total duration of the labeling pulse train, in seconds, corresponding to the temporal width of the labeling bolus for"PCASL"or"CASL". In case all control-
label volumes (or deltam or CBF) have the sameLabelingDuration, a scalar must be specified. In case the control-label volumes (or deltam or cbf) have a different
"LabelingDuration", an array of numbers must be specified, for which anym0scanin the timeseries has a"LabelingDuration"of zero. In case an array of numbers is
provided, its length should be equal to the number of volumes specified in*_aslcontext.tsv. Corresponds to DICOM Tag 0018, 9258ASL Pulse Train Duration.

Schema information:

anyOf **:**

**-** minimum **:** 0
    type **:** number
    unit **:** s
**-** items **:**
    minimum **:** 0
    type **:** number
    unit **:** s
    type **:** array

## LabelingEfficiency (metadata)

Name: Labeling Efficiency

Type: Metadata

Description: Labeling efficiency, specified as a number between zero and one, only if obtained externally (for example phase-contrast based).

Schema information:

exclusiveMinimum **:** 0
type **:** number

## LabelingLocationDescription (metadata).

Name: Labeling Location Description

Type: Metadata

Description: Descriptionofthelocationofthelabelingplane("CASL"or"PCASL")orthelabelingslab("PASL")thatcannotbecapturedbyfieldsLabelingOrientationor
LabelingDistance. Mayincludealinktoananonymizedscreenshotoftheplanningofthelabelingslab/planewithrespecttotheimagingslaborslices*_asllabeling.jpg.


Based on DICOM macro C.8.13.5.14.

Schema information:

type **:** string

## LabelingOrientation (metadata)

Name: Labeling Orientation

Type: Metadata

Description: Orientation of the labeling plane ((P)CASL) or slab (PASL). The direction cosines of a normal vector perpendicular to the ASL labeling slab or plane with
respect to the patient. Corresponds to DICOM Tag 0018, 9255ASL Slab Orientation.

Schema information:

items **:**
type **:** number
type **:** array

## LabelingPulseAverageB1 (metadata).

Name: Labeling Pulse Average B1

Type: Metadata

Description: The average B1-field strength of the RF labeling pulses, in microteslas. As an alternative,"LabelingPulseFlipAngle"can be provided.

Schema information:

exclusiveMinimum **:** 0
type **:** number
unit **:** uT

## LabelingPulseAverageGradient (metadata)

Name: Labeling Pulse Average Gradient

Type: Metadata

Description: The average labeling gradient, in milliteslas per meter.

Schema information:


exclusiveMinimum **:** 0
type **:** number
unit **:** mT/m

## LabelingPulseDuration (metadata).

Name: Labeling Pulse Duration

Type: Metadata

Description: Duration of the individual labeling pulses, in milliseconds.

Schema information:

exclusiveMinimum **:** 0
type **:** number
unit **:** ms

## LabelingPulseFlipAngle (metadata)

Name: Labeling Pulse Flip Angle

Type: Metadata

Description: The flip angle of a single labeling pulse, in degrees, which can be given as an alternative to"LabelingPulseAverageB1".

Schema information:

exclusiveMinimum **:** 0
maximum **:** 360
type **:** number
unit **:** degree

## LabelingPulseInterval (metadata)

Name: Labeling Pulse Interval

Type: Metadata

Description: Delay between the peaks of the individual labeling pulses, in milliseconds.

Schema information:


exclusiveMinimum **:** 0
type **:** number
unit **:** ms

## LabelingPulseMaximumGradient (metadata)

Name: Labeling Pulse Maximum Gradient

Type: Metadata

Description: The maximum amplitude of the gradient switched on during the application of the labeling RF pulse(s), in milliteslas per meter.

Schema information:

exclusiveMinimum **:** 0
type **:** number
unit **:** mT/m

## LabelingSlabThickness (metadata)

Name: Labeling Slab Thickness

Type: Metadata

Description: Thickness of the labeling slab in millimeters. For non-selective FAIR a zero is entered. Corresponds to DICOM Tag 0018, 9254ASL Slab Thickness.

Schema information:

exclusiveMinimum **:** 0
type **:** number
unit **:** mm

## Levels (metadata)

Name: Levels

Type: Metadata

Description: For categorical variables: An object of possible values (keys) and their descriptions (values).

Schema information:

additionalProperties **:**
type **:** string
type **:** object


## License (metadata).

Name: License

Type: Metadata

Description: The license for the dataset. The use of license name abbreviations is RECOMMENDED for specifying a license (see Licenses). The corresponding full license
text MAY be specified in an additionalLICENSEfile.

Schema information:

type **:** string

## LongName (metadata).

Name: Long Name

Type: Metadata

Description: Long (unabbreviated) name of the column.

Schema information:

type **:** string

## LookLocker (metadata)

Name: Look Locker

Type: Metadata

Description: Boolean indicating if a Look-Locker readout is used.

Schema information:

type **:** boolean

## M0Estimate (metadata)

Name: M0Estimate

Type: Metadata

Description: A single numerical whole-brain M0 value (referring to the M0 of blood), only if obtained externally (for example retrieved from CSF in a separate measure-
ment).


Schema information:

exclusiveMinimum **:** 0
type **:** number

## M0Type (metadata)

Name: M0Type

Type: Metadata

Allowed values:Separate,Included,Estimate,Absent

Description: Describes the presence of M0 information."Separate"means that a separate*_m0scan.nii[.gz]is present."Included"means that an m0scan volume is
contained within the current*_asl.nii[.gz]."Estimate"means that a single whole-brain M0 value is provided."Absent"means that no specific M0 information is
present.

Schema information:

type **:** string

## M0map (suffixes).

Name: Equilibrium magnetization (M0) map

Type: Suffix

Format:<entities>_M0map.<extension>

Description: In arbitrary units (arbitrary). A common quantitative MRI (qMRI) fitting variable that represents the amount of magnetization at thermal equilibrium. M0
maps are RECOMMENDED to use this suffix if generated by qMRI applications (for example, variable flip angle T1 mapping).

Schema information:

unit **:** arbitrary

## MAGNChannelCount (metadata).

Name: Magnetometer Channel Count

Type: Metadata

Description: Number of magnetometer channels.

Schema information:


minimum **:** 0
type **:** integer

## MEGChannelCount (metadata).

Name: MEG Channel Count

Type: Metadata

Description: Number of MEG channels (for example, 275 ).

Schema information:

minimum **:** 0
type **:** integer

## MEGCoordinateSystem (metadata).

Name: MEG Coordinate System

Type: Metadata

Allowed values: CTF, ElektaNeuromag, 4DBti, KitYokogawa, ChietiItab, Other, CapTrak, EEGLAB, EEGLAB-HJ, Other, ICBM452AirSpace, ICBM452Warp5Space,
IXI549Space,fsaverage,fsaverageSym, fsLR,MNIColin27,MNI152Lin,MNI152NLin2009aSym,MNI152NLin2009bSym,MNI152NLin2009cSym,MNI152NLin2009aAsym,
MNI152NLin2009bAsym,MNI152NLin2009cAsym,MNI152NLin6Sym,MNI152NLin6ASym,MNI305,NIHPD,OASIS30AntsOASISAnts,OASIS30Atropos,Talairach,UNCInfant,
fsaverage3,fsaverage4,fsaverage5,fsaverage6,fsaveragesym,UNCInfant0V21,UNCInfant1V21,UNCInfant2V21,UNCInfant0V22,UNCInfant1V22,UNCInfant2V22,
UNCInfant0V23,UNCInfant1V23,UNCInfant2V23

Description: DefinesthecoordinatesystemfortheMEGsensors. SeetheCoordinateSystemsAppendixforalistofrestrictedkeywordsforcoordinatesystems. If"Other",
provide definition of the coordinate system in"MEGCoordinateSystemDescription".

Schema information:

type **:** string

## MEGCoordinateSystemDescription (metadata)

Name: MEG Coordinate System Description

Type: Metadata

Description: Free-form text description of the coordinate system. May also include a link to a documentation page or paper describing the system in greater detail.

Schema information:


type **:** string

## MEGCoordinateUnits (metadata).

Name: MEG Coordinate Units

Type: Metadata

Allowed values:m,mm,cm,n/a

Description: Units of the coordinates of"MEGCoordinateSystem".

Schema information:

type **:** string

## MEGRE (suffixes)

Name: Multi-echo Gradient Recalled Echo

Type: Suffix

Format:<entities>_MEGRE.<extension>

Description: Anatomical gradient echo images acquired at different echo times. Please note that this suffix is not intended for the logical grouping of images acquired
using an Echo Planar Imaging (EPI) readout.

## MEGREFChannelCount (metadata)

Name: MEGREF Channel Count

Type: Metadata

Description: NumberofMEGreferencechannels(forexample, 23 ). Forsystemswithoutsuchchannels(forexample,NeuromagVectorview),MEGREFChannelCountshould
be set to 0.

Schema information:

minimum **:** 0
type **:** integer


## MESE (suffixes).

Name: Multi-echo Spin Echo

Type: Suffix

Format:<entities>_MESE.<extension>

Description: The MESE method involves multiple spin echo images acquired at different echo times and is primarily used for T2 mapping. Please note that this suffix is
not intended for the logical grouping of images acquired using an Echo Planar Imaging (EPI) readout.

## MP2RAGE (suffixes).

Name: Magnetization Prepared Two Gradient Echoes

Type: Suffix

Format:<entities>_MP2RAGE.<extension>

Description: TheMP2RAGEmethodisaspecialprotocolthatcollectsseveralimagesatdifferentflipanglesandinversiontimestocreateaparametricT1mapbycombining
the magnitude and phase images (Marques et al. 2010).

## MPE (suffixes)

Name: Multi-photon excitation microscopy

Type: Suffix

Format:<entities>_MPE.<extension>

Description: Multi-photon excitation microscopy imaging data

## MPM (suffixes)

Name: Multi-parametric Mapping

Type: Suffix

Format:<entities>_MPM.<extension>

Description: TheMPMapproaches(a.k.ahMRI)involvestheacquisitionofhighly-similaranatomicalimagesthatdifferintermsofapplicationofamagnetizationtransfer
RF pulse (MTon or MToff), flip angle and (optionally) echo time and magnitue/phase parts (Weiskopf et al. 2013). Seeherefor suggested MPM acquisition protocols.


## MRAcquisitionType (metadata)

Name: MR Acquisition Type

Type: Metadata

Allowed values:2D,3D

Description: Type of sequence readout. Corresponds to DICOM Tag 0018, 0023MR Acquisition Type.

Schema information:

type **:** string

## MRTransmitCoilSequence (metadata)

Name: MR Transmit Coil Sequence

Type: Metadata

Description: This is a relevant field if a non-standard transmit coil is used. Corresponds to DICOM Tag 0018, 9049MR Transmit Coil Sequence.

Schema information:

type **:** string

## MTNumberOfPulses (metadata)

Name: MT Number Of Pulses

Type: Metadata

Description: The number of magnetization transfer RF pulses applied before the readout.

Schema information:

type **:** number

## MTOffsetFrequency (metadata)

Name: MT Offset Frequency

Type: Metadata

Description: The frequency offset of the magnetization transfer pulse with respect to the central H1 Larmor frequency in Hertz (Hz).

Schema information:


type **:** number
unit **:** Hz

## MTPulseBandwidth (metadata).

Name: MT Pulse Bandwidth

Type: Metadata

Description: The excitation bandwidth of the magnetization transfer pulse in Hertz (Hz).

Schema information:

type **:** number
unit **:** Hz

## MTPulseDuration (metadata).

Name: MT Pulse Duration

Type: Metadata

Description: Duration of the magnetization transfer RF pulse in seconds.

Schema information:

type **:** number
unit **:** s

## MTPulseShape (metadata)

Name: MT Pulse Shape

Type: Metadata

Allowed values:HARD,GAUSSIAN,GAUSSHANN,SINC,SINCHANN,SINCGAUSS,FERMI

Description: Shape of the magnetization transfer RF pulse waveform. The value"GAUSSHANN"refers to a Gaussian pulse with a Hanning window. The value"SINCHANN"
refers to a sinc pulse with a Hanning window. The value"SINCGAUSS"refers to a sinc pulse with a Gaussian window.

Schema information:

type **:** string


## MTR (suffixes)

Name: Magnetization Transfer Ratio

Type: Suffix

Format:<entities>_MTR.<extension>

Description: This method is to calculate a semi-quantitative magnetization transfer ratio map.

## MTRmap (suffixes).

Name: Magnetization transfer ratio image

Type: Suffix

Format:<entities>_MTRmap.<extension>

Description: In arbitrary units (arbitrary). MTR maps are REQUIRED to use this suffix regardless of the method used to generate them. MTRmap intensity values are
RECOMMENDED to be represented in percentage in the range of 0-100%.

Schema information:

maxValue **:** 100
minValue **:** 0
unit **:** arbitrary

## MTS (suffixes)

Name: Magnetization transfer saturation

Type: Suffix

Format:<entities>_MTS.<extension>

Description: Thismethodistocalculateasemi-quantitativemagnetizationtransfersaturationindexmap. TheMTSmethodinvolvesthreesetsofanatomicalimagesthat
differ in terms of application of a magnetization transfer RF pulse (MTon or MToff) and flip angle (Helms et al. 2008).

## MTState (metadata)

Name: MT State

Type: Metadata

Description: Boolean stating whether the magnetization transfer pulse is applied. Corresponds to DICOM Tag 0018, 9020Magnetization Transfer.


Schema information:

type **:** boolean

## MTVmap (suffixes).

Name: Macromolecular tissue volume (MTV) image

Type: Suffix

Format:<entities>_MTVmap.<extension>

Description: In arbitrary units (arbitrary). MTV maps are REQUIRED to use this suffix regardless of the method used to generate them.

Schema information:

unit **:** arbitrary

## MTsat (suffixes)

Name: Magnetization transfer saturation image

Type: Suffix

Format:<entities>_MTsat.<extension>

Description: In arbitrary units (arbitrary). MTsat maps are REQUIRED to use this suffix regardless of the method used to generate them.

Schema information:

unit **:** arbitrary

## MWFmap (suffixes)

Name: Myelin water fraction image

Type: Suffix

Format:<entities>_MWFmap.<extension>

Description: In arbitrary units (arbitrary). MWF maps are REQUIRED to use this suffix regardless of the method used to generate them. MWF intensity values are
RECOMMENDED to be represented in percentage in the range of 0-100%.

Schema information:


maxValue **:** 100
minValue **:** 0
unit **:** arbitrary

## MagneticFieldStrength (metadata)

Name: Magnetic Field Strength

Type: Metadata

Description: Nominal field strength of MR magnet in Tesla. Corresponds to DICOM Tag 0018, 0087Magnetic Field Strength.

Schema information:

type **:** number

## Magnification (metadata)

Name: Magnification

Type: Metadata

Description: Lensmagnification(forexample: 40 ). IfthefileformatisOME-TIFF,thevalueMUSTbeconsistentwiththe"NominalMagnification"OMEmetadatafield.

Schema information:

exclusiveMinimum **:** 0
type **:** number

## Manual (metadata).

Name: Manual

Type: Metadata

Description: Indicates if the segmentation was performed manually or via an automated process.

Schema information:

type **:** boolean


## Manufacturer (metadata)

Name: Manufacturer

Type: Metadata

Description: Manufacturer of the equipment that produced the measurements.

Schema information:

type **:** string

## ManufacturersModelName (metadata).

Name: Manufacturers Model Name

Type: Metadata

Description: Manufacturer’s model name of the equipment that produced the measurements.

Schema information:

type **:** string

## MatrixCoilMode (metadata).

Name: Matrix Coil Mode

Type: Metadata

Description: (If used) A method for reducing the number of independent channels by combining in analog the signals from multiple coil elements. There are typically
different default modes when using un-accelerated or accelerated (for example,"GRAPPA","SENSE") imaging.

Schema information:

type **:** string

## MaxMovement (metadata)

Name: Max Movement

Type: Metadata

Description: Maximum head movement (in mm) detected during the recording, as measured by the head localisation coils (for example,4.8).

Schema information:


type **:** number
unit **:** mm

## MeasurementToolMetadata (metadata)

Name: Measurement Tool Metadata

Type: Metadata

Description: A description of the measurement tool as a whole. Contains two fields:"Description"and"TermURL". "Description"is a free text description of the
measurement tool."TermURL"is a URL to an entity in an ontology corresponding to this tool.

Schema information:

properties **:**
Description **:**
type **:** string
TermURL **:**
format **:** uri
type **:** string
type **:** object

## MetaboliteAvail (metadata).

Name: Metabolite Available

Type: Metadata

Description: Boolean that specifies if metabolite measurements are available. Iftrue, themetabolite_parent_fractioncolumn MUST be present in the corresponding
*_blood.tsvfile.

Schema information:

type **:** boolean

## MetaboliteMethod (metadata)

Name: Metabolite Method

Type: Metadata

Description: Method used to measure metabolites.

Schema information:


type **:** string

## MetaboliteRecoveryCorrectionApplied (metadata)

Name: Metabolite Recovery Correction Applied

Type: Metadata

Description: Metabolite recovery correction from the HPLC, for tracers where it changes with time postinjection. Iftrue, thehplc_recovery_fractionscolumn MUST
be present in the corresponding*_blood.tsvfile.

Schema information:

type **:** boolean

## MiscChannelCount (metadata)

Name: Misc Channel Count

Type: Metadata

Description: Number of miscellaneous analog channels for auxiliary signals.

Schema information:

minimum **:** 0
type **:** integer

## MixingTime (metadata)

Name: Mixing Time

Type: Metadata

Description: In the context of a stimulated- and spin-echo 3D EPI sequence for B1+ mapping, corresponds to the interval between spin- and stimulated-echo pulses. In
the context of a diffusion-weighted double spin-echo sequence, corresponds to the interval between two successive diffusion sensitizing gradients, specified in seconds.

Schema information:

type **:** number
unit **:** s


## ModeOfAdministration (metadata).

Name: Mode Of Administration

Type: Metadata

Description: Mode of administration of the injection (for example,"bolus","infusion", or"bolus-infusion").

Schema information:

type **:** string

## MolarActivity (metadata)

Name: Molar Activity

Type: Metadata

Description: Molar activity of compound injected. Corresponds to DICOM Tag 0018, 1077Radiopharmaceutical Specific Activity.

Schema information:

type **:** number

## MolarActivityMeasTime (metadata)

Name: Molar Activity Measurement Time

Type: Metadata

Description: Time to which molar radioactivity measurement above applies in the default unit"hh:mm:ss".

Schema information:

format **:** time
type **:** string

## MolarActivityUnits (metadata)

Name: Molar Activity Units

Type: Metadata

Description: Unit of the specified molar radioactivity (for example,"GBq/umol").

Schema information:


format **:** unit
type **:** string

## MultibandAccelerationFactor (metadata)

Name: Multiband Acceleration Factor

Type: Metadata

Description: The multiband factor, for multiband acquisitions.

Schema information:

type **:** number

## MultipartID (metadata)

Name: MultipartID

Type: Metadata

Description: A unique (per participant) label tagging DWI runs that are part of a multipart scan.

Schema information:

type **:** string

## NIRSChannelCount (metadata).

Name: NIRS Channel Count

Type: Metadata

Description: Total number of NIRS channels, including short channels. Corresponds to the number of rows inchannels.tsvwith any NIRS type.

Schema information:

minimum **:** 0
type **:** integer

## NIRSCoordinateProcessingDescription (metadata)

Name: NIRS Coordinate Processing Description


Type: Metadata

Description: Has any post-processing (such as projection) been done on the optode positions (for example,"surface_projection","n/a").

Schema information:

type **:** string

## NIRSCoordinateSystem (metadata).

Name: NIRS Coordinate System

Type: Metadata

Allowed values: CTF, ElektaNeuromag, 4DBti, KitYokogawa, ChietiItab, Other, CapTrak, EEGLAB, EEGLAB-HJ, Other, ICBM452AirSpace, ICBM452Warp5Space,
IXI549Space,fsaverage,fsaverageSym, fsLR,MNIColin27,MNI152Lin,MNI152NLin2009aSym,MNI152NLin2009bSym,MNI152NLin2009cSym,MNI152NLin2009aAsym,
MNI152NLin2009bAsym,MNI152NLin2009cAsym,MNI152NLin6Sym,MNI152NLin6ASym,MNI305,NIHPD,OASIS30AntsOASISAnts,OASIS30Atropos,Talairach,UNCInfant,
fsaverage3,fsaverage4,fsaverage5,fsaverage6,fsaveragesym,UNCInfant0V21,UNCInfant1V21,UNCInfant2V21,UNCInfant0V22,UNCInfant1V22,UNCInfant2V22,
UNCInfant0V23,UNCInfant1V23,UNCInfant2V23

Description: Defines the coordinate system in which the optode positions are expressed.See Appendix VIII for a list of restricted keywords for coordinate systems. If
"Other", a definition of the coordinate system MUST be provided inNIRSCoordinateSystemDescription.

Schema information:

type **:** string

## NIRSCoordinateSystemDescription (metadata)

Name: NIRS Coordinate System Description

Type: Metadata

Description: Free-form text description of the coordinate system. May also include a link to a documentation page or paper describing the system in greater detail.

Schema information:

type **:** string

## NIRSCoordinateUnits (metadata).

Name: NIRS Coordinate Units

Type: Metadata


Allowed values:m,mm,cm,n/a

Description: Units of the coordinates ofNIRSCoordinateSystem.

Schema information:

type **:** string

## NIRSDetectorOptodeCount (metadata)

Name: NIRS Detector Optode Channel Count

Type: Metadata

Description: Number of NIRS detectors. Corresponds to the number of rows inoptodes.tsvwith type"detector".

Schema information:

minimum **:** 1
type **:** integer

## NIRSPlacementScheme (metadata).

Name: NIRS Placement Scheme

Type: Metadata

Description: PlacementschemeofNIRSoptodes. Eitherthenameofastandardizedplacementsystem(forexample,"10-20")oranarrayofstandardizedpositionnames
(for example,["Cz", "Pz"]). This field should only be used if a cap was not used. If a standard cap was used, then it should be specified inCapManufacturerand
CapManufacturersModelNameand this field should be set to"n/a"

Schema information:

anyOf **:**

**-** type **:** string
**-** items **:**
    type **:** string
type **:** array

## NIRSSourceOptodeCount (metadata).

Name: NIRS Source Optode Count

Type: Metadata


Description: Number of NIRS sources. Corresponds to the number of rows inoptodes.tsvwith type"source".

Schema information:

minimum **:** 1
type **:** integer

## NLO (suffixes).

Name: Nonlinear optical microscopy

Type: Suffix

Format:<entities>_NLO.<extension>

Description: Nonlinear optical microscopy imaging data

## Name (metadata).

Name: Name

Type: Metadata

Description: Name of the dataset.

Schema information:

type **:** string

## NegativeContrast (metadata)

Name: Negative Contrast

Type: Metadata

Description:trueorfalsevalue specifying whether increasing voxel intensity (within sample voxels) denotes a decreased value with respect to the contrast suffix. This
is commonly the case when Cerebral Blood Volume is estimated via usage of a contrast agent in conjunction with a T2* weighted acquisition protocol.

Schema information:

type **:** boolean


## None (extensions)

Name: No extension

Type: Extension

Format:<entities>_<suffix>

Description: A file with no extension.

## NonlinearGradientCorrection (metadata)

Name: Nonlinear Gradient Correction

Type: Metadata

Description: Boolean stating if the image saved has been corrected for gradient nonlinearities by the scanner sequence.

Schema information:

type **:** boolean

## NumberOfVolumesDiscardedByScanner (metadata)

Name: Number Of Volumes Discarded By Scanner

Type: Metadata

Description: Number of volumes (”dummy scans”) discarded by the scanner (as opposed to those discarded by the user post hoc) before saving the imaging file. For
example, a sequence that automatically discards the first 4 volumes before saving would have this field as 4. A sequence that does not discard dummy scans would have
this set to 0. Please note that the onsets recorded in theevents.tsvfile should always refer to the beginning of the acquisition of the first volume in the corresponding
imaging file - independent of the value of"NumberOfVolumesDiscardedByScanner"field.

Schema information:

minimum **:** 0
type **:** integer

## NumberOfVolumesDiscardedByUser (metadata)

Name: Number Of Volumes Discarded By User

Type: Metadata


Description: Number of volumes (”dummy scans”) discarded by the user before including the file in the dataset. If possible, including all of the volumes is strongly
recommended. Please note that the onsets recorded in theevents.tsvfile should always refer to the beginning of the acquisition of the first volume in the corresponding
imaging file - independent of the value of"NumberOfVolumesDiscardedByUser"field.

Schema information:

minimum **:** 0
type **:** integer

## NumberShots (metadata)

Name: Number Shots

Type: Metadata

Description: The number of RF excitations needed to reconstruct a slice or volume (may be referred to as partition). Please mind that this is not the same as Echo Train
Lengthwhichdenotesthenumberofk-spacelinescollectedafterexcitationinamulti-echoreadout. Thedatatypearrayisapplicableforspecifyingthisparameterbefore
and after the k-space center is sampled. Please see"NumberShots"metadata field in the qMRI appendix for corresponding calculations.

Schema information:

anyOf **:**

**-** type **:** number
**-** items **:**
    type **:** number
type **:** array

## NumericalAperture (metadata)

Name: Numerical Aperture

Type: Metadata

Description: Lens numerical aperture (for example:1.4). If the file format is OME-TIFF, the value MUST be consistent with theLensNAOME metadata field.

Schema information:

exclusiveMinimum **:** 0
type **:** number

## OCT (suffixes).

Name: Optical coherence tomography


Type: Suffix

Format:<entities>_OCT.<extension>

Description: Optical coherence tomography imaging data

## OMEBigTiff (extensions).

Name: Open Microscopy Environment BigTIFF

Type: Extension

Format:<entities>_<suffix>.ome.btf

Description: ABigTIFFimage file, for very large images.

## OMETiff (extensions)

Name: Open Microscopy Environment Tag Image File Format

Type: Extension

Format:<entities>_<suffix>.ome.tif

Description: AnOME-TIFFimage file.

## OMEZARR (extensions)

Name: OME Next Generation File Format

Type: Extension

Format:<entities>_<suffix>.ome.zarr/

Description: An OME-NGFF file.OME-NGFF is aZarr-based format, organizing data arrays in nested directories. This format was developed by the Open Microscopy
Environment to provide data stream access to very large data.

## OperatingSystem (metadata)

Name: Operating System

Type: Metadata

Description: Operating system used to run the stimuli presentation software (for formatting recommendations, see examples below this table).


Schema information:

type **:** string

## OtherAcquisitionParameters (metadata).

Name: Other Acquisition Parameters

Type: Metadata

Description: Description of other relevant image acquisition parameters.

Schema information:

type **:** string

## PASLType (metadata).

Name: PASL Type

Type: Metadata

Description: Type of the labeling pulse of thePASLlabeling, for example"FAIR","EPISTAR", or"PICORE".

Schema information:

type **:** string

## PC (suffixes)

Name: Phase-contrast microscopy

Type: Suffix

Format:<entities>_PC.<extension>

Description: Phase-contrast microscopy imaging data

## PCASLType (metadata)

Name: PCASL Type

Type: Metadata

Allowed values:balanced,unbalanced


Description: The type of gradient pulses used in thecontrolcondition.

Schema information:

type **:** string

## PD (suffixes)

Name: Proton density image

Type: Suffix

Format:<entities>_PD.<extension>

Description: Ambiguous, may refer to a parametric image or to a conventional image. Change: Replaced byPDworPDmap.

Schema information:

unit **:** arbitrary

## PDT2 (suffixes).

Name: PD and T2 weighted image

Type: Suffix

Format:<entities>_PDT2.<extension>

Description: In arbitrary units (arbitrary). PDw and T2w images acquired using a dual echo FSE sequence through view sharing process (Johnson et al. 1994).

Schema information:

unit **:** arbitrary

## PDT2map (suffixes)

Name: Combined PD/T2 image

Type: Suffix

Format:<entities>_PDT2map.<extension>

Description: In arbitrary units (arbitrary). Combined PD/T2 maps are REQUIRED to use this suffix regardless of the method used to generate them.

Schema information:

unit **:** arbitrary


## PDmap (suffixes)

Name: Proton density image

Type: Suffix

Format:<entities>_PDmap.<extension>

Description: In arbitrary units (arbitrary). PD maps are REQUIRED to use this suffix regardless of the method used to generate them.

Schema information:

unit **:** arbitrary

## PDw (suffixes)

Name: Proton density (PD) weighted image

Type: Suffix

Format:<entities>_PDw.<extension>

Description: In arbitrary units (arbitrary). The contrast of these images is mainly determined by spatial variations in the spin density (1H) of the imaged specimen. In
spin-echosequencesthiscontrastisachievedatshortrepetitionandlongechotimes. Inagradient-echoacquisition,PDweightingdominatesthecontrastatlongrepetition
and short echo times, and at small flip angles.

Schema information:

unit **:** arbitrary

## PLI (suffixes)

Name: Polarized-light microscopy

Type: Suffix

Format:<entities>_PLI.<extension>

Description: Polarized-light microscopy imaging data

## ParallelAcquisitionTechnique (metadata)

Name: Parallel Acquisition Technique

Type: Metadata


Description: The type of parallel imaging used (for example"GRAPPA","SENSE"). Corresponds to DICOM Tag 0018, 9078Parallel Acquisition Technique.

Schema information:

type **:** string

## ParallelReductionFactorInPlane (metadata).

Name: Parallel Reduction Factor In Plane

Type: Metadata

Description: The parallel imaging (for instance, GRAPPA) factor. Use the denominator of the fraction of k-space encoded for each slice. For example, 2 means half of
k-space is encoded. Corresponds to DICOM Tag 0018, 9069Parallel Reduction Factor In-plane.

Schema information:

type **:** number

## PartialFourier (metadata)

Name: Partial Fourier

Type: Metadata

Description: The fraction of partial Fourier information collected. Corresponds to DICOM Tag 0018, 9081Partial Fourier.

Schema information:

type **:** number

## PartialFourierDirection (metadata).

Name: Partial Fourier Direction

Type: Metadata

Description: The direction where only partial Fourier information was collected. Corresponds to DICOM Tag 0018, 9036Partial Fourier Direction.

Schema information:

type **:** string


## PharmaceuticalDoseAmount (metadata).

Name: Pharmaceutical Dose Amount

Type: Metadata

Description: Dose amount of pharmaceutical coadministered with tracer.

Schema information:

anyOf **:**

**-** type **:** number
**-** items **:**
    type **:** number
type **:** array

## PharmaceuticalDoseRegimen (metadata)

Name: Pharmaceutical Dose Regimen

Type: Metadata

Description: Details of the pharmaceutical dose regimen. Either adequate description or short-code relating to regimen documented elsewhere (for example,"single
oral bolus").

Schema information:

type **:** string

## PharmaceuticalDoseTime (metadata)

Name: Pharmaceutical Dose Time

Type: Metadata

Description: Time of administration of pharmaceutical dose, relative to time zero. For an infusion, this should be a vector with two elements specifying the start
and end of the infusion period. For more complex dose regimens, the regimen description should be complete enough to enable unambiguous interpretation of
"PharmaceuticalDoseTime". Unit format of the specified pharmaceutical dose time MUST be seconds.

Schema information:

anyOf **:**

**-** type **:** number
    unit **:** s
**-** items **:**


```
type : number
unit : s
type : array
```
## PharmaceuticalDoseUnits (metadata)

Name: Pharmaceutical Dose Units

Type: Metadata

Description: Unit format relating to pharmaceutical dose (for example,"mg"or"mg/kg").

Schema information:

format **:** unit
type **:** string

## PharmaceuticalName (metadata).

Name: Pharmaceutical Name

Type: Metadata

Description: Name of pharmaceutical coadministered with tracer.

Schema information:

type **:** string

## PhaseEncodingDirection (metadata)

Name: Phase Encoding Direction

Type: Metadata

Allowed values:i,j,k,i-,j-,k-

Description: The lettersi,j,kcorrespond to the first, second and third axis of the data in the NIFTI file. The polarity of the phase encoding is assumed to go from zero
index to maximum index unless-sign is present (then the order is reversed - starting from the highest index instead of zero).PhaseEncodingDirectionis defined as the
directionalongwhichphaseiswasmodulatedwhichmayresultinvisibledistortions. NotethatthisisnotthesameastheDICOMtermInPlanePhaseEncodingDirection
which can haveROWorCOLvalues.

Schema information:

type **:** string


## PhotoDescription (metadata)

Name: Photo Description

Type: Metadata

Description: Description of the photo.

Schema information:

type **:** string

## PixelSize (metadata).

Name: Pixel Size

Type: Metadata

Description: A2-or3-numberarrayofthephysicalsizeofapixel,either[PixelSizeX, PixelSizeY]or[PixelSizeX, PixelSizeY, PixelSizeZ],whereXisthewidth,
YtheheightandZthedepth. IfthefileformatisOME-TIFF,thesevaluesneedtobeconsistentwithPhysicalSizeX,PhysicalSizeYandPhysicalSizeZOMEmetadata
fields, after converting inPixelSizeUnitsaccording toPhysicalSizeXunit,PhysicalSizeYunitandPhysicalSizeZunitOME fields.

Schema information:

items **:**
minimum **:** 0
type **:** number
maxItems **:** 3
minItems **:** 2
type **:** array

## PixelSizeUnits (metadata)

Name: Pixel Size Units

Type: Metadata

Allowed values:mm,um,nm

Description: Unit format of the specified"PixelSize". MUST be one of:"mm"(millimeter),"um"(micrometer) or"nm"(nanometer).

Schema information:

type **:** string


## PlasmaAvail (metadata).

Name: Plasma Avail

Type: Metadata

Description: Boolean that specifies if plasma measurements are available.

Schema information:

type **:** boolean

## PlasmaFreeFraction (metadata)

Name: Plasma Free Fraction

Type: Metadata

Description: Measured free fraction in plasma, meaning the concentration of free compound in plasma divided by total concentration of compound in plasma (Units:
0-100%).

Schema information:

maximum **:** 100
minimum **:** 0
type **:** number

## PlasmaFreeFractionMethod (metadata)

Name: Plasma Free Fraction Method

Type: Metadata

Description: Method used to estimate free fraction.

Schema information:

type **:** string

## PostLabelingDelay (metadata)

Name: Post Labeling Delay

Type: Metadata


Description: This is the postlabeling delay (PLD) time, in seconds, after the end of the labeling (for"CASL"or"PCASL") or middle of the labeling pulse (for"PASL") until
the middle of the excitation pulse applied to the imaging slab (for 3D acquisition) or first slice (for 2D acquisition). Can be a number (for a single-PLD time series) or an
array of numbers (for multi-PLD and Look-Locker). In the latter case, the array of numbers contains the PLD of each volume, namely eachcontrolandlabel, in the
acquisition order. Any image within the time-series without a PLD, for example anm0scan, is indicated by a zero. Based on DICOM Tags 0018, 9079Inversion Times
and 0018, 0082InversionTime.

Schema information:

anyOf **:**

**-** exclusiveMinimum **:** 0
    type **:** number
    unit **:** s
**-** items **:**
    exclusiveMinimum **:** 0
    type **:** number
    unit **:** s
    type **:** array

## PowerLineFrequency (metadata).

Name: Power Line Frequency

Type: Metadata

Description: Frequency (in Hz) of the power grid at the geographical location of the instrument (for example, 50 or 60 ).

Schema information:

anyOf **:**

**-** exclusiveMinimum **:** 0
    type **:** number
    unit **:** Hz
**-** enum **:**
    **-** n/a
    type **:** string

## PromptRate (metadata)

Name: Prompt Rate

Type: Metadata

Description: Prompt rate for each frame (same units asUnits, for example,"Bq/mL").


Schema information:

items **:**
type **:** number
type **:** array

## PulseSequenceDetails (metadata).

Name: Pulse Sequence Details

Type: Metadata

Description: Information beyond pulse sequence type that identifies the specific pulse sequence used (for example,"Standard Siemens Sequence distributed with
the VB17 software","Siemens WIP ### version #.##,"or"Sequence written by X using a version compiled on MM/DD/YYYY").

Schema information:

type **:** string

## PulseSequenceType (metadata).

Name: Pulse Sequence Type

Type: Metadata

Description: Ageneraldescriptionofthepulsesequenceusedforthescan(forexample,"MPRAGE","Gradient Echo EPI","Spin Echo EPI","Multiband gradient echo
EPI").

Schema information:

type **:** string

## Purity (metadata)

Name: Purity

Type: Metadata

Description: Purity of the radiolabeled compound (between 0 and 100%).

Schema information:

maximum **:** 100
minimum **:** 0
type **:** number


## R1map (suffixes)

Name: Longitudinal relaxation rate image

Type: Suffix

Format:<entities>_R1map.<extension>

Description: In seconds-1 (1/s). R1 maps (R1 = 1/T1) are REQUIRED to use this suffix regardless of the method used to generate them.

Schema information:

unit **:** 1/s

## R2map (suffixes)

Name: True transverse relaxation rate image

Type: Suffix

Format:<entities>_R2map.<extension>

Description: In seconds-1 (1/s). R2 maps (R2 = 1/T2) are REQUIRED to use this suffix regardless of the method used to generate them.

Schema information:

unit **:** 1/s

## R2starmap (suffixes).

Name: Observed transverse relaxation rate image

Type: Suffix

Format:<entities>_R2starmap.<extension>

Description: In seconds-1 (1/s). R2-star maps (R2star = 1/T2star) are REQUIRED to use this suffix regardless of the method used to generate them.

Schema information:

unit **:** 1/s

## RB1COR (suffixes)

Name: RB1COR

Type: Suffix


Format:<entities>_RB1COR.<extension>

Description: Lowresolutionimagesacquiredbythebodycoil(inthegantryofthescanner)andtheheadcoilusingidenticalacquisitionparameterstogenerateacombined
sensitivity map as described inPapp et al. (2016).

## RB1map (suffixes)

Name: RF receive sensitivity map

Type: Suffix

Format:<entities>_RB1map.<extension>

Description: Inarbitraryunits(arbitrary). Radiofrequency(RF)receive(B1-)sensitivitymapsareREQUIREDtousethissuffixregardlessofthemethodusedtogenerate
them. RB1map intensity values are RECOMMENDED to be represented as percent multiplicative factors such that Amplitudeeffective = B1-intensity*Amplitudeideal.

Schema information:

unit **:** arbitrary

## README (files).

Name: README

Type: Files And Directories

Description: A REQUIRED text file,README, SHOULD describe the dataset in more detail. TheREADMEfile MUST be either in ASCII or UTF-8 encoding and MAY have
one of the extensions:.md(Markdown),.rst(reStructuredText), or.txt. A BIDS dataset MUST NOT contain more than oneREADMEfile (with or without extension) at
its root directory. BIDS does not make any recommendations with regards to theMarkdown flavorand does not validate the syntax of Markdown and reStructuredText.
TheREADMEfile SHOULD be structured such that its contents can be easily understood even if the used format is not rendered. A guideline for creating a goodREADMEfile
can be found in thebids-starter-kit.

Schema information:

file_type **:** regular

## RandomRate (metadata)

Name: Random Rate

Type: Metadata

Description: Random rate for each frame (same units as"Units", for example,"Bq/mL").

Schema information:


items **:**
type **:** number
type **:** array

## RawSources (metadata)

Name: Raw Sources

Type: Metadata

Description: A list of paths relative to dataset root pointing to the BIDS-Raw file(s) that were used in the creation of this derivative. This field is DEPRECATED, and this
metadata SHOULD be recorded in theSourcesfield using BIDS URIs to distinguish sources from different datasets.

Schema information:

items **:**
format **:** dataset_relative
type **:** string
type **:** array

## ReceiveCoilActiveElements (metadata)

Name: Receive Coil Active Elements

Type: Metadata

Description: Information describing the active/selected elements of the receiver coil. This does not correspond to a tag in the DICOM ontology. The vendor-defined
terminology for active coil elements can go in this field.

Schema information:

type **:** string

## ReceiveCoilName (metadata)

Name: Receive Coil Name

Type: Metadata

Description: Information describing the receiver coil. Corresponds to DICOM Tag 0018, 1250Receive Coil Name, although not all vendors populate that DICOM Tag, in
which case this field can be derived from an appropriate private DICOM field.

Schema information:


type **:** string

## ReconFilterSize (metadata)

Name: Recon Filter Size

Type: Metadata

Description: Kernel size of post-recon filter (FWHM) in default units"mm".

Schema information:

anyOf **:**

**-** type **:** number
    unit **:** mm
**-** items **:**
    type **:** number
    unit **:** mm
    type **:** array

## ReconFilterType (metadata)

Name: Recon Filter Type

Type: Metadata

Description: Type of post-recon smoothing (for example,["Shepp"]).

Schema information:

anyOf **:**

**-** type **:** string
**-** items **:**
    type **:** string
type **:** array

## ReconMethodImplementationVersion (metadata).

Name: Recon Method Implementation Version

Type: Metadata

Description: Identification for the software used, such as name and version.


Schema information:

type **:** string

## ReconMethodName (metadata).

Name: Recon Method Name

Type: Metadata

Description: Reconstruction method or algorithm (for example,"3d-op-osem").

Schema information:

type **:** string

## ReconMethodParameterLabels (metadata)

Name: Recon Method Parameter Labels

Type: Metadata

Description: Names of reconstruction parameters (for example,["subsets", "iterations"]).

Schema information:

items **:**
type **:** string
type **:** array

## ReconMethodParameterUnits (metadata)

Name: Recon Method Parameter Units

Type: Metadata

Description: Unit of reconstruction parameters (for example,["none", "none"]).

Schema information:

items **:**
format **:** unit
type **:** string
type **:** array


## ReconMethodParameterValues (metadata)

Name: Recon Method Parameter Values

Type: Metadata

Description: Values of reconstruction parameters (for example,[21, 3]).

Schema information:

items **:**
type **:** number
type **:** array

## RecordingDuration (metadata)

Name: Recording Duration

Type: Metadata

Description: Length of the recording in seconds (for example, 3600 ).

Schema information:

type **:** number
unit **:** s

## RecordingType (metadata)

Name: Recording Type

Type: Metadata

Allowed values:continuous,epoched,discontinuous

Description: Defines whether the recording is"continuous","discontinuous", or"epoched", where"epoched"is limited to time windows about events of interest (for
example, stimulus presentations or subject responses).

Schema information:

type **:** string

## ReferencesAndLinks (metadata)

Name: References And Links


Type: Metadata

Description: List of references to publications that contain information on the dataset. A reference may be textual or a URI.

Schema information:

items **:**
type **:** string
type **:** array

## RepetitionTime (metadata)

Name: Repetition Time

Type: Metadata

Description: The time in seconds between the beginning of an acquisition of one volume and the beginning of acquisition of the volume following it (TR). When used in
thecontextoffunctionalacquisitionsthisparameterbestcorrespondstoDICOMTag0020,0110: the”timedeltabetweenimagesinadynamicoffunctionalsetofimages”
but may also be found inDICOM Tag 0018, 0080: ”the period of time in msec between the beginning of a pulse sequence and the beginning of the succeeding (essentially
identical) pulse sequence”. This definition includes time between scans (when no data has been acquired) in case of sparse acquisition schemes. This value MUST be
consistent with the ’pixdim[4]’ field (after accounting for units stored in ’xyzt_units’ field) in the NIfTI header. This field is mutually exclusive with VolumeTiming.

Schema information:

exclusiveMinimum **:** 0
type **:** number
unit **:** s

## RepetitionTimeExcitation (metadata)

Name: Repetition Time Excitation

Type: Metadata

Description: The interval, in seconds, between two successive excitations. DICOM Tag 0018, 0080best refers to this parameter. This field may be used together with
the"RepetitionTimePreparation"for certain use cases, such asMP2RAGE. UseRepetitionTimeExcitation(in combination with"RepetitionTimePreparation"if
needed)foranatomyimagingdataratherthan"RepetitionTime"asitisalreadydefinedastheamountoftimethatittakestoacquireasinglevolumeinthetaskimaging
data section.

Schema information:

minimum **:** 0
type **:** number
unit **:** s


## RepetitionTimePreparation (metadata)

Name: Repetition Time Preparation

Type: Metadata

Description: The interval, in seconds, that it takes a preparation pulse block to re-appear at the beginning of the succeeding (essentially identical) pulse sequence block.
The data type number may apply to files from any MRI modality concerned with a single value for this field. The data type array provides a value for each volume in a
4D dataset and should only be used when the volume timing is critical for interpretation of the data, such as in ASL.

Schema information:

anyOf **:**

**-** minimum **:** 0
    type **:** number
    unit **:** s
**-** items **:**
    minimum **:** 0
    type **:** number
    unit **:** s
    type **:** array

## Resolution (metadata).

Name: Resolution

Type: Metadata

Description: Specifiestheinterpretationoftheresolutionkeyword. Ifanobjectisused,thenthekeysshouldbevaluesfortheresentityandvaluesshouldbedescriptions
of thoseresvalues.

Schema information:

anyOf **:**

**-** type **:** string
**-** additionalProperties **:**
    type **:** string
type **:** object

## S0map (suffixes)

Name: Observed signal amplitude (S0) image

Type: Suffix


Format:<entities>_S0map.<extension>

Description: Inarbitraryunits(arbitrary). Foramulti-echo(typicallyfMRI)sequence,S0mapsindexthebaselinesignalbeforeexponential(T2-star)signaldecay. Inother
words: the exponential of the intercept for a linear decay model across log-transformed echos. For more information, please see, for example,the tedana documentation.
S0 maps are RECOMMENDED to use this suffix if derived from an ME-FMRI dataset.

## SEEGChannelCount (metadata)

Name: SEEG Channel Count

Type: Metadata

Description: Number of SEEG channels.

Schema information:

minimum **:** 0
type **:** integer

## SEM (suffixes).

Name: Scanning electron microscopy

Type: Suffix

Format:<entities>_SEM.<extension>

Description: Scanning electron microscopy imaging data

## SPIM (suffixes)

Name: Selective plane illumination microscopy

Type: Suffix

Format:<entities>_SPIM.<extension>

Description: Selective plane illumination microscopy imaging data

## SR (suffixes).

Name: Super-resolution microscopy

Type: Suffix


Format:<entities>_SR.<extension>

Description: Super-resolution microscopy imaging data

## SampleEmbedding (metadata)

Name: Sample Embedding

Type: Metadata

Description: Description of the tissue sample embedding (for example:"Epoxy resin").

Schema information:

type **:** string

## SampleEnvironment (metadata)

Name: Sample Environment

Type: Metadata

Allowed values:in vivo,ex vivo,in vitro

Description: Environment in which the sample was imaged. MUST be one of:"in vivo","ex vivo"or"in vitro".

Schema information:

type **:** string

## SampleExtractionInstitution (metadata).

Name: Sample Extraction Institution

Type: Metadata

Description: The name of the institution in charge of the extraction of the sample, if different from the institution in charge of the equipment that produced the image.

Schema information:

type **:** string


## SampleExtractionProtocol (metadata).

Name: Sample Extraction Protocol

Type: Metadata

Description: Description of the sample extraction protocol or URI (for example fromprotocols.io).

Schema information:

type **:** string

## SampleFixation (metadata)

Name: Sample Fixation

Type: Metadata

Description: Description of the tissue sample fixation (for example:"4% paraformaldehyde, 2% glutaraldehyde").

Schema information:

type **:** string

## SampleOrigin (metadata)

Name: Sample Origin

Type: Metadata

Allowed values:blood,saliva,brain,csf,breast milk,bile,amniotic fluid,other biospecimen

Description: Describes from which tissue the genetic information was extracted.

Schema information:

type **:** string

## SamplePrimaryAntibody (metadata).

Name: Sample Primary Antibody

Type: Metadata


Description: Description(s) of the primary antibody used for immunostaining. Either anRRIDor the name, supplier and catalogue number of a commercial antibody.
Fornon-commercialantibodieseitheranRRIDorthehost-animalandimmunogenused(forexamples:"RRID:AB_2122563"or"Rabbit anti-Human HTR5A Polyclonal
Antibody, Invitrogen, Catalog # PA1-2453"). MAY be an array of strings if different antibodies are used in each channel of the file.

Schema information:

anyOf **:**

**-** type **:** string
**-** items **:**
    type **:** string
type **:** array

## SampleSecondaryAntibody (metadata).

Name: Sample Secondary Antibody

Type: Metadata

Description: Description(s)ofthesecondaryantibodyusedforimmunostaining. EitheranRRIDorthename,supplierandcataloguenumberofacommercialantibody. For
non-commercialantibodieseitheranRRIDorthehost-animalandimmunogenused(forexamples:"RRID:AB_228322"or"Goat anti-Mouse IgM Secondary Antibody,
Invitrogen, Catalog # 31172"). MAY be an array of strings if different antibodies are used in each channel of the file.

Schema information:

anyOf **:**

**-** type **:** string
**-** items **:**
    type **:** string
type **:** array

## SampleStaining (metadata)

Name: Sample Staining

Type: Metadata

Description: Description(s) of the tissue sample staining (for example:"Osmium"). MAY be an array of strings if different stains are used in each channel of the file (for
example:["LFB", "PLP"]).

Schema information:

anyOf **:**

**-** type **:** string
**-** items **:**


```
type : string
type : array
```
## SamplingFrequency sense 1 (metadata)

Name: Sampling Frequency

Type: Metadata

Description: Sampling frequency (in Hz) of all the data in the recording, regardless of their type (for example, 2400 ).

Schema information:

type **:** number
unit **:** Hz

## SamplingFrequency sense 2 (metadata)

Name: Sampling Frequency

Type: Metadata

Description: Sampling frequency (in Hz) of all the data in the recording, regardless of their type (for example, 2400 ).

Schema information:

anyOf **:**

**-** type **:** number
    unit **:** Hz
**-** enum **:**
    **-** n/a
    type **:** string

## ScaleFactor (metadata)

Name: Scale Factor

Type: Metadata

Description: Scale factor for each frame. This field MUST be defined if the imaging data (.nii[.gz]) are scaled. If this field is not defined, then it is assumed that the
scaling factor is 1. Defining this field when the scaling factor is 1 is RECOMMENDED, for the sake of clarity.

Schema information:


items **:**
type **:** number
type **:** array

## ScanDate (metadata).

Name: Scan Date

Type: Metadata

Description: Date of scan in the format"YYYY-MM-DD[Z]". This field is DEPRECATED, and this metadata SHOULD be recorded in theacq_timecolumn of the corre-
sponding Scans file.

Schema information:

format **:** date
type **:** string

## ScanOptions (metadata)

Name: Scan Options

Type: Metadata

Description: Parameters of ScanningSequence. Corresponds to DICOM Tag 0018, 0022Scan Options.

Schema information:

anyOf **:**

**-** type **:** string
**-** items **:**
    type **:** string
type **:** array

## ScanStart (metadata)

Name: Scan Start

Type: Metadata

Description: Time of start of scan with respect toTimeZeroin the default unit seconds.

Schema information:


type **:** number
unit **:** s

## ScanningSequence (metadata).

Name: Scanning Sequence

Type: Metadata

Description: Description of the type of data acquired. Corresponds to DICOM Tag 0018, 0020Scanning Sequence.

Schema information:

anyOf **:**

**-** type **:** string
**-** items **:**
    type **:** string
type **:** array

## ScatterFraction (metadata)

Name: Scatter Fraction

Type: Metadata

Description: Scatter fraction for each frame (Units: 0-100%).

Schema information:

items **:**
maximum **:** 100
minimum **:** 0
type **:** number
type **:** array

## SequenceName (metadata)

Name: Sequence Name

Type: Metadata

Description: Manufacturer’s designation of the sequence name. Corresponds to DICOM Tag 0018, 0024Sequence Name.

Schema information:


type **:** string

## SequenceVariant (metadata)

Name: Sequence Variant

Type: Metadata

Description: Variant of the ScanningSequence. Corresponds to DICOM Tag 0018, 0021Sequence Variant.

Schema information:

anyOf **:**

**-** type **:** string
**-** items **:**
    type **:** string
type **:** array

## ShortChannelCount (metadata).

Name: Short Channel Count

Type: Metadata

Description: The number of short channels. 0 indicates no short channels.

Schema information:

minimum **:** 0
type **:** integer

## SinglesRate (metadata)

Name: Singles Rate

Type: Metadata

Description: Singles rate for each frame (same units asUnits, for example,"Bq/mL").

Schema information:

items **:**
type **:** number
type **:** array


## SkullStripped (metadata)

Name: Skull Stripped

Type: Metadata

Description: Whether the volume was skull stripped (non-brain voxels set to zero) or not.

Schema information:

type **:** boolean

## SliceEncodingDirection (metadata).

Name: Slice Encoding Direction

Type: Metadata

Allowed values:i,j,k,i-,j-,k-

Description: TheaxisoftheNIfTIdataalongwhichsliceswereacquired,andthedirectioninwhich"SliceTiming"isdefinedwithrespectto.i,j,kidentifierscorrespond
to the first, second and third axis of the data in the NIfTI file. A-sign indicates that the contents of"SliceTiming"are defined in reverse order - that is, the first entry
corresponds to the slice with the largest index, and the final entry corresponds to slice index zero. When present, the axis defined by"SliceEncodingDirection"needs
to be consistent with theslice_dimfield in the NIfTI header. When absent, the entries in"SliceTiming"must be in the order of increasing slice index as defined by the
NIfTI header.

Schema information:

type **:** string

## SliceThickness (metadata).

Name: Slice Thickness

Type: Metadata

Description: Slice thickness of the tissue sample in the unit micrometers ("um") (for example: 5 ).

Schema information:

exclusiveMinimum **:** 0
type **:** number
unit **:** um


## SliceTiming (metadata)

Name: Slice Timing

Type: Metadata

Description: Thetimeatwhicheachslicewasacquiredwithineachvolume(frame)oftheacquisition. Slicetimingisnotsliceorder--rather,itisalistoftimescontaining
the time (in seconds) of each slice acquisition in relation to the beginning of volume acquisition. The list goes through the slices along the slice axis in the slice encoding
dimension (see below). Note that to ensure the proper interpretation of the"SliceTiming"field, it is important to check if the OPTIONALSliceEncodingDirection
exists. In particular, if"SliceEncodingDirection"is negative, the entries in"SliceTiming"are defined in reverse order with respect to the slice axis, such that the final
entry in the"SliceTiming"list is the time of acquisition of slice 0. Without this parameter slice time correction will not be possible.

Schema information:

items **:**
minimum **:** 0
type **:** number
unit **:** s
type **:** array

## SoftwareFilters (metadata)

Name: Software Filters

Type: Metadata

Description: Objectof temporal software filters applied, or"n/a"if the data is not available. Each key-value pair in the JSON object is a name of the filter and
an object in which its parameters are defined as key-value pairs (for example,{"Anti-aliasing filter": {"half-amplitude cutoff (Hz)": 500, "Roll-off":
"6dB/Octave"}}).

Schema information:

anyOf **:**

**-** additionalProperties **:**
    type **:** object
type **:** object
**-** enum **:**
    **-** n/a
    type **:** string

## SoftwareName (metadata).

Name: Software Name


Type: Metadata

Description: Name of the software that was used to present the stimuli.

Schema information:

type **:** string

## SoftwareRRID (metadata).

Name: SoftwareRRID

Type: Metadata

Description: Research Resource Identifierof the software that was used to present the stimuli. Examples: The RRID for Psychtoolbox is ’SCR_002881’, and that of
PsychoPy is ’SCR_006571’.

Schema information:

format **:** rrid
type **:** string

## SoftwareVersion (metadata)

Name: Software Version

Type: Metadata

Description: Version of the software that was used to present the stimuli.

Schema information:

type **:** string

## SoftwareVersions (metadata)

Name: Software Versions

Type: Metadata

Description: Manufacturer’s designation of software version of the equipment that produced the measurements.

Schema information:

type **:** string


## SourceDatasets (metadata)

Name: Source Datasets

Type: Metadata

Description: Used to specify the locations and relevant attributes of all source datasets. Valid keys in each object include"URL","DOI"(see URI), and"Version"with
stringvalues.

Schema information:

items **:**
properties **:**
DOI **:**
type **:** string
URL **:**
format **:** uri
type **:** string
Version **:**
type **:** string
type **:** object
type **:** array

## SourceType (metadata)

Name: Source Type

Type: Metadata

Description: Typeofsource. Preferablyaspecificmodel/partnumberissupplied. Thisisafreeformdescription,butthefollowingkeywordsaresuggested:"LED","LASER",
"VCSEL". If individual channels have different SourceType, then the field here should be specified as ”mixed” and this column should be included in optodes.tsv.

Schema information:

type **:** string

## Sources (metadata).

Name: Sources

Type: Metadata

Description: A list of files with the paths specified using BIDS URIs; these files were directly used in the creation of this derivative data file. For example, if a derivative A
is used in the creation of another derivative B, which is in turn used to generate C in a chain of A->B->C, C should only list B in"Sources", and B should only list A in


"Sources". However, in case both X and Y are directly used in the creation of Z, then Z should list X and Y in"Sources", regardless of whether X was used to generate
Y. Using paths specified relative to the dataset root is BIDS URIs.

Schema information:

items **:**
format **:** dataset_relative
type **:** string
type **:** array

## SpatialReference (metadata)

Name: Spatial Reference

Type: Metadata

Description: For images with a single reference, the value MUST be a single string. For images with multiple references, such as surface and volume references, a JSON
object MUST be used.

Schema information:

anyOf **:**

**-** enum **:**
    **-** orig
    type **:** string
**-** format **:** uri
    type **:** string
**-** format **:** dataset_relative
    type **:** string
**-** additionalProperties **:**
    anyOf **:**
    **-** enum **:**
       **-** orig
       type **:** string
    **-** format **:** uri
       type **:** string
    **-** format **:** dataset_relative
       type **:** string
    type **:** object


## SpecificRadioactivity (metadata)

Name: Specific Radioactivity

Type: Metadata

Description: Specific activity of compound injected. Note this is not required for an FDG acquisition, since it is not available, and SHOULD be set to **"n/a"**.

Schema information:

anyOf **:**

**-** type **:** number
**-** enum **:**
    **-** n/a
    type **:** string

## SpecificRadioactivityMeasTime (metadata)

Name: Specific Radioactivity Measurement Time

Type: Metadata

Description: Time to which specific radioactivity measurement above applies in the default unit"hh:mm:ss".

Schema information:

format **:** time
type **:** string

## SpecificRadioactivityUnits (metadata).

Name: Specific Radioactivity Units

Type: Metadata

Description: Unit format of specified specific radioactivity (for example,"Bq/g"). Note this is not required for an FDG acquisition, since it is not available, and SHOULD
be set to **"n/a"**.

Schema information:

anyOf **:**

**-** format **:** unit
    type **:** string
**-** enum **:**


**-** n/a
type **:** string

## SpoilingGradientDuration (metadata)

Name: Spoiling Gradient Duration

Type: Metadata

Description: The duration of the spoiler gradient lobe in seconds. The duration of a trapezoidal lobe is defined as the summation of ramp-up and plateau times.

Schema information:

type **:** number
unit **:** s

## SpoilingGradientMoment (metadata).

Name: Spoiling Gradient Moment

Type: Metadata

Description: Zeroth moment of the spoiler gradient lobe in millitesla times second per meter (mT.s/m).

Schema information:

type **:** number
unit **:** mT.s/m

## SpoilingRFPhaseIncrement (metadata)

Name: Spoiling RF Phase Increment

Type: Metadata

Description: The amount of incrementation described in degrees, which is applied to the phase of the excitation pulse at each TR period for achieving RF spoiling.

Schema information:

type **:** number
unit **:** degrees


## SpoilingState (metadata).

Name: Spoiling State

Type: Metadata

Description: Boolean stating whether the pulse sequence uses any type of spoiling strategy to suppress residual transverse magnetization.

Schema information:

type **:** boolean

## SpoilingType (metadata)

Name: Spoiling Type

Type: Metadata

Allowed values:RF,GRADIENT,COMBINED

Description: Specifies which spoiling method(s) are used by a spoiled sequence.

Schema information:

type **:** string

## StartTime (metadata)

Name: Start Time

Type: Metadata

Description: Start time in seconds in relation to the start of acquisition of the first data sample in the corresponding neural dataset (negative values are allowed).

Schema information:

type **:** number
unit **:** s

## StationName (metadata).

Name: Station Name

Type: Metadata

Description: Institution defined name of the machine that produced the measurements.


Schema information:

type **:** string

## StimulusPresentation (metadata).

Name: Stimulus Presentation

Type: Metadata

Description: Object containing key-value pairs related to the software used to present the stimuli during the experiment, specifically: "OperatingSystem",
"SoftwareName","SoftwareRRID","SoftwareVersion"and"Code". See table below for more information.

Schema information:

properties **:**
Code **:**
description **:** '[URI](../02-common-principles.md#uniform-resource-indicator)

```
of the code used to present the stimuli.
```
```
Persistent identifiers such as DOIs are preferred.
```
```
If multiple versions of code may be hosted at the same location,
```
```
revision-specific URIs are recommended.
```
```
'
display_name : Code
format : uri
name : Code
type : string
OperatingSystem :
description : 'Operating system used to run the stimuli presentation software
```
```
(for formatting recommendations, see examples below this table).
```
```
'
display_name : Operating System
name : OperatingSystem
type : string
SoftwareName :
```

```
description : 'Name of the software that was used to present the stimuli.
```
```
'
display_name : Software Name
name : SoftwareName
type : string
SoftwareRRID :
description : '[Research Resource Identifier](https://scicrunch.org/resources)
of the
```
```
software that was used to present the stimuli.
```
```
Examples: The RRID for Psychtoolbox is''SCR_002881'',
```
```
and that of PsychoPy is ''SCR_006571''.
```
```
'
display_name : SoftwareRRID
format : rrid
name : SoftwareRRID
type : string
SoftwareVersion :
description : 'Version of the software that was used to present the stimuli.
```
'
display_name **:** Software Version
name **:** SoftwareVersion
type **:** string
type **:** object

## SubjectArtefactDescription (metadata).

Name: Subject Artefact Description

Type: Metadata

Description: Freeform description of the observed subject artefact and its possible cause (for example,"Vagus Nerve Stimulator","non-removable implant"). If this
field is set to"n/a", it will be interpreted as absence of major source of artifacts except cardiac and blinks.

Schema information:

type **:** string


## T1map (suffixes)

Name: Longitudinal relaxation time image

Type: Suffix

Format:<entities>_T1map.<extension>

Description: Inseconds(s). T1mapsareREQUIREDtousethissuffixregardlessofthemethodusedtogeneratethem. SeethisinteractivebookonT1mappingforfurther
reading on T1-mapping.

Schema information:

unit **:** s

## T1rho (suffixes).

Name: T1 in rotating frame (T1 rho) image

Type: Suffix

Format:<entities>_T1rho.<extension>

Description: In seconds (s). T1-rho maps are REQUIRED to use this suffix regardless of the method used to generate them.

Schema information:

unit **:** s

## T1w (suffixes).

Name: T1-weighted image

Type: Suffix

Format:<entities>_T1w.<extension>

Description: In arbitrary units (arbitrary). The contrast of these images is mainly determined by spatial variations in the longitudinal relaxation time of the imaged
specimen. In spin-echo sequences this contrast is achieved at relatively short repetition and echo times. To achieve this weighting in gradient-echo images, again, short
repetition and echo times are selected; however, at relatively large flip angles. Another common approach to increase T1 weighting in gradient-echo images is to add an
inversion preparation block to the beginning of the imaging sequence (for example,TurboFLASHorMP-RAGE).

Schema information:

unit **:** arbitrary


## T2map (suffixes)

Name: True transverse relaxation time image

Type: Suffix

Format:<entities>_T2map.<extension>

Description: In seconds (s). T2 maps are REQUIRED to use this suffix regardless of the method used to generate them.

Schema information:

unit **:** s

## T2star (suffixes)

Name: T2* image

Type: Suffix

Format:<entities>_T2star.<extension>

Description: Ambiguous, may refer to a parametric image or to a conventional image. Change: Replaced byT2starworT2starmap.

Schema information:

anyOf **:**

**-** unit **:** arbitrary
**-** unit **:** s

## T2starmap (suffixes).

Name: Observed transverse relaxation time image

Type: Suffix

Format:<entities>_T2starmap.<extension>

Description: In seconds (s). T2-star maps are REQUIRED to use this suffix regardless of the method used to generate them.

Schema information:

unit **:** s


## T2starw (suffixes)

Name: T2star weighted image

Type: Suffix

Format:<entities>_T2starw.<extension>

Description: In arbitrary units (arbitrary). The contrast of these images is mainly determined by spatial variations in the (observed) transverse relaxation time of the
imagedspecimen. Inspin-echosequences, thiseffectisnegatedastheexcitationisfollowedbyaninversionpulse. Thecontrastofgradient-echoimagesnativelydepends
on T2-star effects. However, for T2-star variation to dominate the image contrast, gradient-echo acquisitions are carried out at long repetition and echo times, and at
small flip angles.

Schema information:

unit **:** arbitrary

## T2w (suffixes).

Name: T2-weighted image

Type: Suffix

Format:<entities>_T2w.<extension>

Description: In arbitrary units (arbitrary). The contrast of these images is mainly determined by spatial variations in the (true) transverse relaxation time of the imaged
specimen. Inspin-echosequencesthiscontrastisachievedatrelativelylongrepetitionandechotimes. Generally,gradientechosequencesarenotthemostsuitableoption
for achieving T2 weighting, as their contrast natively depends on T2-star rather than on T2.

Schema information:

unit **:** arbitrary

## TB1AFI (suffixes).

Name: TB1AFI

Type: Suffix

Format:<entities>_TB1AFI.<extension>

Description: Thismethod(Yarnykh2007)calculatesaB1+mapfromtwoimagesacquiredatinterleaved(two)TRswithidenticalRFpulsesusingasteady-statesequence.


## TB1DAM (suffixes).

Name: TB1DAM

Type: Suffix

Format:<entities>_TB1DAM.<extension>

Description: The double-angle B1+ method (Insko and Bolinger 1993) is based on the calculation of the actual angles from signal ratios, collected by two acquisitions at
different nominal excitation flip angles. Common sequence types for this application include spin echo and echo planar imaging.

## TB1EPI (suffixes).

Name: TB1EPI

Type: Suffix

Format:<entities>_TB1EPI.<extension>

Description: This B1+ mapping method (Jiru and Klose 2006) is based on two EPI readouts to acquire spin echo (SE) and stimulated echo (STE) images at multiple flip
angles in one sequence, used in the calculation of deviations from the nominal flip angle.

## TB1RFM (suffixes)

Name: TB1RFM

Type: Suffix

Format:<entities>_TB1RFM.<extension>

Description: The result of a Siemensrf_mapproduct sequence. This sequence produces two images. The first image appears like an anatomical image and the second
output is a scaled flip angle map.

## TB1SRGE (suffixes)

Name: TB1SRGE

Type: Suffix

Format:<entities>_TB1SRGE.<extension>

Description: Saturation-prepared with 2 rapid gradient echoes (SA2RAGE) uses a ratio of two saturation recovery images with different time delays, and a simulated
look-up table to estimate B1+ (Eggenschwiler et al. 2011). This sequence can also be used in conjunction with MP2RAGE T1 mapping to iteratively improve B1+ and T1
map estimation (Marques & Gruetter 2013).


## TB1TFL (suffixes)

Name: TB1TFL

Type: Suffix

Format:<entities>_TB1TFL.<extension>

Description: TheresultofaSiemenstfl_b1_mapproductsequence. Thissequenceproducestwoimages. Thefirstimageappearslikeananatomicalimageandthesecond
output is a scaled flip angle map.

## TB1map (suffixes)

Name: RF transmit field image

Type: Suffix

Format:<entities>_TB1map.<extension>

Description: In arbitrary units (arbitrary). Radio frequency (RF) transmit (B1+) field maps are REQUIRED to use this suffix regardless of the method used to generate
them. TB1mapintensityvaluesareRECOMMENDEDtoberepresentedaspercentmultiplicativefactorssuchthatFlipAngleeffective=B1+intensity*FlipAnglenominal

Schema information:

unit **:** arbitrary

## TEM (suffixes)

Name: Transmission electron microscopy

Type: Suffix

Format:<entities>_TEM.<extension>

Description: Transmission electron microscopy imaging data

## TaskDescription (metadata).

Name: Task Description

Type: Metadata

Description: Longer description of the task.

Schema information:


type **:** string

## TaskName (metadata).

Name: Task Name

Type: Metadata

Description: Name of the task. No two tasks should have the same name. The task label included in the file name is derived from this"TaskName"field by removing all
non-alphanumeric characters (that is, all except those matching[0-9a-zA-Z]). For example"TaskName" "faces n-back"will correspond to task labelfacesnback.

Schema information:

type **:** string

## TermURL (metadata)

Name: TermURL

Type: Metadata

Description: URL pointing to a formal definition of this type of data in an ontology available on the web.

Schema information:

type **:** string

## TimeZero (metadata)

Name: Time Zero

Type: Metadata

Description: Time zero to which all scan and/or blood measurements have been adjusted to, in the unit ”hh:mm:ss”. This should be equal to"InjectionStart"or
"ScanStart".

Schema information:

format **:** time
type **:** string


## TissueDeformationScaling (metadata)

Name: Tissue Deformation Scaling

Type: Metadata

Description: Estimateddeformationofthetissue,givenasapercentageoftheoriginaltissuesize(forexamples: forashrinkageof3%,thevalueis 97 ;andforanexpansion
of 100%, the value is 200 ).

Schema information:

exclusiveMinimum **:** 0
type **:** number

## TissueOrigin (metadata).

Name: Tissue Origin

Type: Metadata

Allowed values:gray matter,white matter,csf,meninges,macrovascular,microvascular

Description: Describes the type of tissue analyzed for"SampleOrigin" brain.

Schema information:

type **:** string

## TotalAcquiredPairs (metadata).

Name: Total Acquired Pairs

Type: Metadata

Description: The total number of acquiredcontrol-labelpairs. A single pair consists of a singlecontroland a singlelabelimage.

Schema information:

exclusiveMinimum **:** 0
type **:** number

## TotalReadoutTime (metadata)

Name: Total Readout Time

Type: Metadata


Description: This is actually the ”effective” total readout time, defined as the readout duration, specified in seconds, that would have generated data with the given level
of distortion. It is NOT the actual, physical duration of the readout train. If"EffectiveEchoSpacing"has been properly computed, it is justEffectiveEchoSpacing *
(ReconMatrixPE - 1).

Schema information:

type **:** number
unit **:** s

## TracerMolecularWeight (metadata)

Name: Tracer Molecular Weight

Type: Metadata

Description: Accurate molecular weight of the tracer used.

Schema information:

type **:** number

## TracerMolecularWeightUnits (metadata)

Name: Tracer Molecular Weight Units

Type: Metadata

Description: Unit of the molecular weights measurement (for example,"g/mol").

Schema information:

format **:** unit
type **:** string

## TracerName (metadata).

Name: Tracer Name

Type: Metadata

Description: Name of the tracer compound used (for example,"CIMBI-36")

Schema information:

type **:** string


## TracerRadLex (metadata).

Name: Tracer Rad Lex

Type: Metadata

Description: ID of the tracer compound from the RadLex Ontology.

Schema information:

type **:** string

## TracerRadionuclide (metadata).

Name: Tracer Radionuclide

Type: Metadata

Description: Radioisotope labelling tracer (for example,"C11").

Schema information:

type **:** string

## TracerSNOMED (metadata).

Name: TracerSNOMED

Type: Metadata

Description: ID of the tracer compound from the SNOMED Ontology (subclass of Radioactive isotope).

Schema information:

type **:** string

## TriggerChannelCount (metadata)

Name: Trigger Channel Count

Type: Metadata

Description: Number of channels for digital (TTL bit level) triggers.

Schema information:


minimum **:** 0
type **:** integer

## TubingLength (metadata).

Name: Tubing Length

Type: Metadata

Description: The length of the blood tubing, from the subject to the detector in meters.

Schema information:

type **:** number
unit **:** m

## TubingType (metadata).

Name: Tubing Type

Type: Metadata

Description: Description of the type of tubing used, ideally including the material and (internal) diameter.

Schema information:

type **:** string

## TwoPE (suffixes)

Name: 2-photon excitation microscopy

Type: Suffix

Format:<entities>_2PE.<extension>

Description: 2-photon excitation microscopy imaging data

## Type (metadata)

Name: Type

Type: Metadata


Allowed values:Brain,Lesion,Face,ROI

Description: Short identifier of the mask. The value"Brain"refers to a brain mask. The value"Lesion"refers to a lesion mask. The value"Face"refers to a face mask.
The value"ROI"refers to a region of interest mask.

Schema information:

type **:** string

## UNIT1 (suffixes)

Name: Homogeneous (flat) T1-weighted MP2RAGE image

Type: Suffix

Format:<entities>_UNIT1.<extension>

Description: Inarbitraryunits(arbitrary). UNIT1imagesareREQUIREDtousethissuffixregardlessofthemethodusedtogeneratethem. Notethatalthoughthisimage
isT1-weighted,regionswithoutMRsignalwillcontainwhitesalt-and-peppernoisethatmostsegmentationalgorithmswillfailon. Therefore,itisimportanttodissociate
it fromT1w. Please seeMP2RAGEspecific notes in the qMRI appendix for further information.

## Units (metadata)

Name: Units

Type: Metadata

Description: Measurement units for the associated file. SI units in CMIXF formatting are RECOMMENDED (see Units).

Schema information:

format **:** unit
type **:** string

## VFA (suffixes)

Name: Variable flip angle

Type: Suffix

Format:<entities>_VFA.<extension>

Description: TheVFAmethodinvolvesatleasttwospoiledgradientecho(SPGR)ofsteady-statefreeprecession(SSFP)imagesacquiredatdifferentflipangles. Depending
on the provided metadata fields and the sequence type, data may be eligible for DESPOT1, DESPOT2 and their variants (Deoni et al. 2005).


## VascularCrushing (metadata).

Name: Vascular Crushing

Type: Metadata

Description: Boolean indicating if Vascular Crushing is used. Corresponds to DICOM Tag 0018, 9259ASL Crusher Flag.

Schema information:

type **:** boolean

## VascularCrushingVENC (metadata)

Name: Vascular Crushing VENC

Type: Metadata

Description: The crusher gradient strength, in centimeters per second. Specify either one number for the total time-series, or provide an array of numbers, for example
when using QUASAR, using the value zero to identify volumes for whichVascularCrushingwas turned off. Corresponds to DICOM Tag 0018, 925AASL Crusher Flow
Limit.

Schema information:

anyOf **:**

**-** type **:** number
    unit **:** cm/s
**-** items **:**
    type **:** number
    unit **:** cm/s
    type **:** array

## VolumeTiming (metadata)

Name: Volume Timing

Type: Metadata

Description: The time at which each volume was acquired during the acquisition. It is described using a list of times referring to the onset of each volume in the BOLD
series. The list must have the same length as the BOLD series, and the values must be non-negative and monotonically increasing. This field is mutually exclusive with
"RepetitionTime"and"DelayTime". If defined, this requires acquisition time (TA) be defined via either"SliceTiming"or"AcquisitionDuration"be defined.

Schema information:


items **:**
type **:** number
unit **:** s
minItems **:** 1
type **:** array

## WholeBloodAvail (metadata)

Name: Whole Blood Avail

Type: Metadata

Description: Boolean that specifies if whole blood measurements are available. Iftrue, thewhole_blood_radioactivitycolumn MUST be present in the corresponding
*_blood.tsvfile.

Schema information:

type **:** boolean

## WithdrawalRate (metadata)

Name: Withdrawal Rate

Type: Metadata

Description: The rate at which the blood was withdrawn from the subject. The unit of the specified withdrawal rate should be in"mL/s".

Schema information:

type **:** number
unit **:** mL/s

## abbreviation (columns)

Name: Abbreviation

Type: Column

Description: The unique label abbreviation

Schema information:

type **:** string


## acq_time sense 1 (columns)

Name: Scan acquisition time

Type: Column

Description: Acquisition time refers to when the first data point in each run was acquired. Furthermore, if this header is provided, the acquisition times of all files from
the same recording MUST be identical. Datetime format and their anonymization are described in Units.

Schema information:

format **:** datetime
type **:** string

## acq_time sense 2 (columns)

Name: Session acquisition time

Type: Column

Description: Acquisition time refers to when the first data point of the first run was acquired. Datetime format and their anonymization are described in Units.

Schema information:

format **:** datetime
type **:** string

## acquisition (entities)

Name: Acquisition

Type: Entity

Description: Theacq-<label>entitycorrespondstoacustomlabeltheuserMAYusetodistinguishadifferentsetofparametersusedforacquiringthesamemodality.For
example, this should be used when a study includes two T1w images - one full brain low resolution and one restricted field of view but high resolution. In such case two
files could have the following names:sub-01_acq-highres_T1w.nii.gzandsub-01_acq-lowres_T1w.nii.gz; however, the user is free to choose any other label than
highresandlowresas long as they are consistent across subjects and sessions.In case different sequences are used to record the same modality (for example,RAREand
FLASHfor T1w) this field can also be used to make that distinction. The level of detail at which the distinction is made (for example, just betweenRAREandFLASH, or
betweenRARE,FLASH, andFLASHsubsampled) remains at the discretion of the researcher.

Schema information:

format **:** label
type **:** string


## age (columns).

Name: Subject age

Type: Column

Description: Numeric value in years (float or integer value).

Schema information:

type **:** number
unit **:** year

## anat (datatypes)

Name: Anatomical Magnetic Resonance Imaging

Type: Datatype

Description: Magnetic resonance imaging sequences designed to characterize static, anatomical features.

## angio (suffixes)

Name: Angiogram

Type: Suffix

Format:<entities>_angio.<extension>

Description: Magnetic resonance angiography sequences focus on enhancing the contrast of blood vessels (generally arteries, but sometimes veins) against other tissue
types.

## asl (suffixes).

Name: Arterial Spin Labeling

Type: Suffix

Format:<entities>_asl.<extension>

Description: The complete ASL time series stored as a 4D NIfTI file in the original acquisition order, with possible volume types including: control, label, m0scan, deltam,
cbf.


## aslcontext (suffixes)

Name: Arterial Spin Labeling Context

Type: Suffix

Format:<entities>_aslcontext.<extension>

Description: A TSV file defining the image types for volumes in an associated ASL file.

## asllabeling (suffixes)

Name: ASL Labeling Screenshot

Type: Suffix

Format:<entities>_asllabeling.<extension>

Description: An anonymized screenshot of the planning of the labeling slab/plane with respect to the imaging slab or slices*_asllabeling.jpg. Based on DICOM macro
C.8.13.5.14.

## atlas (entities).

Name: Atlas

Type: Entity

Description: Theatlas-<label>key/value pair corresponds to a custom label the user MAY use to distinguish a different atlas used for similar type of data.This entity
is only applicable to derivative data.

Schema information:

format **:** label
type **:** string

## ave (extensions)

Name: AVE

Type: Extension

Format:<entities>_<suffix>.ave

Description: File containing data averaged by segments of interest.Used by KIT, Yokogawa, and Ricoh MEG systems.


## bdf (extensions)

Name: Biosemi Data Format

Type: Extension

Format:<entities>_<suffix>.bdf

Description: ABiosemiData Format file.Each recording consists of a single.bdffile.bdf+files are permitted. The capital.BDFextension MUST NOT be used.

## beh (datatypes).

Name: Behavioral Data

Type: Datatype

Description: Behavioral data.

## beh (modalities)

Name: Behavioral experiments

Type: Modalities

Description: Behavioral data acquired without accompanying neuroimaging data.

## beh (suffixes)

Name: Behavioral recording

Type: Suffix

Format:<entities>_beh.<extension>

Description: Behavioral recordings from tasks. These files are similar to events files, but do not include the"onset"and"duration"columns that are mandatory for
events files.

## bids_uri (formats)

Name: BIDS uniform resource indicator

Type: Format

Regular expression:bids:[0-9a-zA-Z/#:\?\_\-\.]+


Description: ABIDSuniformresourceindicator.Thevalidationforthisformatisminimal. Itsimplyensuresthatthevalueisastringwithanycharactersthatmayappear
in a valid URI, starting with ”bids:”.

## blood (suffixes)

Name: Blood recording data

Type: Suffix

Format:<entities>_blood.<extension>

Description: Blood measurements of radioactivity stored in tabular files and located in thepet/directory along with the corresponding PET data.

## bold (suffixes).

Name: Blood-Oxygen-Level Dependent image

Type: Suffix

Format:<entities>_bold.<extension>

Description: Blood-Oxygen-Level Dependent contrast (specialized T2* weighting)

## boolean (formats)

Name: Boolean

Type: Format

Regular expression:(true|false)

Description: A boolean. Must be either ”true” or ”false”.

## bval (extensions)

Name: FSL-Format Gradient Amplitudes

Type: Extension

Format:<entities>_<suffix>.bval

Description: A space-delimited file containing gradient directions (b-vectors) of diffusion measurement.Thebvalfile contains the b-values (in s/mm2) corresponding to
the volumes in the relevant NIfTI file, with 0 designating b=0 volumes.


## bvec (extensions).

Name: FSL-Format Gradient Directions

Type: Extension

Format:<entities>_<suffix>.bvec

Description: A space-delimited file containing gradient directions (b-vectors) of diffusion measurement.This file contains 3 rows with N space-delimited floating-point
numbers, corresponding to the N volumes in the corresponding NIfTI file.The first row contains the x elements, the second row contains the y elements and the third row
containsthezelementsofaunitvectorinthedirectionoftheapplieddiffusiongradient, wherethei-thelementsineachrowcorrespondtogethertothei-thvolume, with
[0,0,0]fornon-diffusion-weighted(alsocalledb=0orlow-b)volumes.FollowingtheFSLformat forthebvecspecification, thecoordinatesystemoftheb vectorsMUST
bedefinedwithrespecttothecoordinatesystemdefinedbytheheaderofthecorresponding_dwiNIfTIfileandnotthescanner’sdevicecoordinatesystem(seeCoordinate
systems). The most relevant limitation imposed by this choice is that the gradient information cannot be directly stored in this format if the scanner generates b-vectors
in scanner coordinates.

## cardiac (columns).

Name: Cardiac measurement

Type: Column

Description: continuous pulse measurement

Schema information:

type **:** number

## cbv (suffixes)

Name: Cerebral blood volume image

Type: Suffix

Format:<entities>_cbv.<extension>

Description: Cerebral Blood Volume contrast (specialized T2* weighting or difference between T1 weighted images)

## ceagent (entities)

Name: Contrast Enhancing Agent

Type: Entity


Description: Thece-<label>entity can be used to distinguish sequences using different contrast enhanced images. The label is the name of the contrast agent.This
entity represents the"ContrastBolusIngredient"metadata field. Therefore, if thece-<label>entity is present in a filename,"ContrastBolusIngredient"MAY also
be added in the JSON file, with the same label.

Schema information:

format **:** label
type **:** string

## channels (suffixes)

Name: Channels File

Type: Suffix

Format:<entities>_channels.<extension>

Description: Channel information.

## chn (extensions)

Name: KRISS CHN

Type: Extension

Format:<entities>_<suffix>.chn

Description: A file generated by KRISS MEG systems containing the position of the center of the MEG coils.Each experimental run on the KRISS system produces a file
with extension.kdf. Additional files that may be available in the same directory include the digitized positions of the head points (\_digitizer.txt), the position of the
center of the MEG coils (.chn), and the event markers (.trg).

## chunk (entities).

Name: Chunk

Type: Entity

Description: Thechunk-<index>key/valuepairisusedtodistinguishbetweendifferentregions,2Dimagesor3Dvolumesfiles,ofthesamephysicalsamplewithdifferent
fields of view acquired in the same imaging experiment.

Schema information:

format **:** index
type **:** string


## code (files).

Name: Code

Type: Files And Directories

Description: A directory in which to store any code (for example the one used to generate the derivatives from the raw data). See the Code section for more information.

Schema information:

file_type **:** directory

## color (columns).

Name: Color label

Type: Column

Description: Hexadecimal. Label color for visualization.

Schema information:

type **:** string
unit **:** hexadecimal

## con (extensions)

Name: KIT/Yokogawa/Ricoh Continuous Data

Type: Extension

Format:<entities>_<suffix>.con

Description: Raw continuous data from a KIT/Yokogawa/Ricoh MEG system.Successor to the.sqdextension for raw continuous data.

## coordsystem (suffixes)

Name: Coordinate System File

Type: Suffix

Format:<entities>_coordsystem.<extension>

Description: A JSON document specifying the coordinate system(s) used for the MEG, EEG, head localization coils, and anatomical landmarks.


## dat (extensions).

Name: MEG Fine-Calibration Format

Type: Extension

Format:<entities>_<suffix>.dat

Description: A fine-calibration file used for Neuromag/Elekta/MEGIN MEG recording hardware.

## data_acquisition (common_principles).

Name: Data acquisition

Type: Common Principle

Description: A continuous uninterrupted block of time during which a brain scanning instrument was acquiring data according to particular scanning sequence/protocol.

## data_type (common_principles).

Name: Data type

Type: Common Principle

Description: A functional group of different types of data. Data files are contained in a directory named for the data type. In raw datasets, the data type directory is
nested inside subject and (optionally) session directories. BIDS defines the following data types: 1.func(task based and resting state functional MRI) 2.dwi(diffusion
weighted imaging) 3.fmap(field inhomogeneity mapping data such as field maps) 4.anat(structural imaging such as T1, T2, PD, and so on) 5.perf(perfusion) 6.meg
(magnetoencephalography) 7.eeg(electroencephalography) 8.ieeg(intracranial electroencephalography) 9.beh(behavioral) 10.pet(positron emission tomography)
11.micr(microscopy) 12.nirs(near infrared spectroscopy)

## dataset (common_principles)

Name: Dataset

Type: Common Principle

Description: A set of neuroimaging and behavioral data acquired for a purpose of a particular study. A dataset consists of data acquired from one or more subjects,
possibly from multiple sessions.

## dataset_description (files)

Name: Dataset Description


Type: Files And Directories

Description: The filedataset_description.jsonis a JSON file describing the dataset.

Schema information:

file_type **:** regular

## dataset_relative (formats).

Name: Path relative to the BIDS dataset directory

Type: Format

Regular expression:(?!/)[0-9a-zA-Z/\_\-\.]+

Description: A path to a file, relative to the dataset directory.The validation for this format is minimal. It simply ensures that the value is a string with any characters
that may appear in a valid path, without starting with ”/” (an absolute path).

## date (formats)

Name: Date

Type: Format

Regular expression:[0-9]{4}-[0-9]{2}-[0-9]{2}([A-Z]{2,4})?

Description: A date in the form"YYYY-MM-DD[Z]", where [Z] is an optional, valid timezone code.

## datetime (formats)

Name: Datetime

Type: Format

Regular expression:[0-9]{4}-[0-9]{2}-[0-9]{2}T(?:2[0-3]|[01][0-9]):[0-5][0-9]:[0-5][0-9](\.[0-9]{1,6})?([A-Z]{2,4})?

Description: A datetime in the form"YYYY-MM-DDThh:mm:ss[.000000][Z]", where [.000000] is an optional subsecond resolution between 1 and 6 decimal points, and [Z]
is an optional, valid timezone code.

## defacemask (suffixes)

Name: Defacing Mask


Type: Suffix

Format:<entities>_defacemask.<extension>

Description: A binary mask that was used to remove facial features from an anatomical MRI image.

## density (entities)

Name: Density

Type: Entity

Description: Density of non-parametric surfaces.This entity represents the"Density"metadata field. Therefore, if theden-<label>entity is present in a filename,
"Density"MUST also be added in the JSON file, to provide interpretation.This entity is only applicable to derivative data.

Schema information:

format **:** label
type **:** string

## deprecated (common_principles)

Name: DEPRECATED

Type: Common Principle

Description: A ”deprecated” entity or metadata field SHOULD NOT be used in the generation of new datasets. It remains in the standard in order to preserve the
interpretability of existing datasets. Validating software SHOULD warn when deprecated practices are detected and provide a suggestion for updating the dataset to
preserve the curator’s intent.

## derivatives (files)

Name: Derivative data

Type: Files And Directories

Description: Derivative data (for example preprocessed files). See the relevant section for more information.

Schema information:

file_type **:** directory


## derived_from (columns)

Name: Derived from

Type: Column

Description:sample-<label>entity from which a sample is derived, for example a slice of tissue (sample-02) derived from a block of tissue (sample-01).

Schema information:

type **:** string

## description (entities)

Name: Description

Type: Entity

Description: When necessary to distinguish two files that do not otherwise have a distinguishing entity, thedesc-<label>entity SHOULD be used.This entity is only
applicable to derivative data.

Schema information:

format **:** label
type **:** string

## description sense 1 (columns)

Name: Description

Type: Column

Description: Brief free-text description of the channel, or other information of interest.

Schema information:

type **:** string

## description sense 2 (columns)

Name: Description

Type: Column

Description: Free-form text description of the optode, or other information of interest.


Schema information:

type **:** string

## detector sense 1 (columns).

Name: Detector Name

Type: Column

Description: Name of the detector as specified in the*_optodes.tsvfile.n/afor channels that do not contain NIRS signals (for example, acceleration).

Schema information:

anyOf **:**

**-** type **:** string
**-** enum **:**
    **-** n/a
    type **:** string

## detector_type (columns).

Name: Detector Type

Type: Column

Description: The type of detector. Only to be used if the fieldDetectorTypein*_nirs.jsonis set tomixed.

Schema information:

anyOf **:**

**-** type **:** string

## dimension (columns).

Name: Dimension

Type: Column

Description: Size of the group (grid/strip/probe) that this electrode belongs to. Must be of form[AxB]with the smallest dimension first (for example,[1x8]).

Schema information:

type **:** string


## direction (entities)

Name: Phase-Encoding Direction

Type: Entity

Description: Thedir-<label>entitycanbesettoanarbitraryalphanumericlabel(forexample,dir-LRordir-AP)todistinguishdifferentphase-encodingdirections.This
entity represents the"PhaseEncodingDirection"metadata field. Therefore, if thedir-<label>entity is present in a filename,"PhaseEncodingDirection"MUST be
defined in the associated metadata. Please note that the<label>does not need to match the actual value of the field.

Schema information:

format **:** label
type **:** string

## dlabelnii (extensions).

Name: CIFTI-2 Dense Label File

Type: Extension

Format:<entities>_<suffix>.dlabel.nii

Description: A CIFTI-2 dense label file.This extension may only be used in derivative datasets.

## dseg (suffixes).

Name: Discrete Segmentation

Type: Suffix

Format:<entities>_dseg.<extension>

Description: A discrete segmentation.This suffix may only be used in derivative datasets.

## duration (columns).

Name: Event duration

Type: Column

Description: Duration of the event (measured from onset) in seconds. Must always be either zero or positive (orn/aif unavailable). A ”duration” value of zero implies
that the delta function or event is so short as to be effectively modeled as an impulse.

Schema information:


anyOf **:**

**-** minimum **:** 0
    type **:** number
    unit **:** s
**-** enum **:**
    **-** n/a
    type **:** string

## dwi (datatypes).

Name: Diffusion-Weighted Imaging

Type: Datatype

Description: Diffusion-weighted imaging (DWI).

## dwi (suffixes)

Name: Diffusion-weighted image

Type: Suffix

Format:<entities>_dwi.<extension>

Description: Diffusion-weighted imaging contrast (specialized T2 weighting).

## echo (entities).

Name: Echo

Type: Entity

Description: If files belonging to an entity-linked file collection are acquired at different echo times, theecho-<index>entity MUST be used to distinguish individual
files.This entity represents the"EchoTime"metadata field. Therefore, if theecho-<index>entity is present in a filename,"EchoTime"MUST be defined in the associated
metadata. Please note that the<index>denotes the number/index (in the form of a nonnegative integer), not the"EchoTime"value of the separate JSON file.

Schema information:

format **:** index
type **:** string


## edf (extensions).

Name: European Data Format

Type: Extension

Format:<entities>_<suffix>.edf

Description: AEuropean data formatfile.Each recording consists of a single.edf`` file. [edf+](https://www.edfplus.info/specs/edfplus.html) files are
permitted. The capital.EDF‘ extension MUST NOT be used.

## eeg (datatypes).

Name: Electroencephalography

Type: Datatype

Description: Electroencephalography

## eeg (extensions).

Name: BrainVision Binary Data

Type: Extension

Format:<entities>_<suffix>.eeg

Description: A binary data file in theBrainVision Core Data Format. These files come in three-file sets, including a.vhdr, a.vmrk, and a.eegfile.

## eeg (modalities).

Name: Electroencephalography

Type: Modalities

Description: Data acquired with EEG.

## eeg (suffixes)

Name: Electroencephalography

Type: Suffix

Format:<entities>_eeg.<extension>


```
Description: Electroencephalography recording data.
```
## electrodes (suffixes).

```
Name: Electrodes
Type: Suffix
Format:<entities>_electrodes.<extension>
Description: File that gives the location of (i)EEG electrodes.
```
## epi (suffixes)

```
Name: EPI
Type: Suffix
Format:<entities>_epi.<extension>
Description: The phase-encoding polarity (PEpolar) technique combines two or more Spin Echo EPI scans with different phase encoding directions to estimate the under-
lying inhomogeneity/deformation map.
```
## event (common_principles)

Name: Event
Type: Common Principle
Description: Somethingthathappensormaybeperceivedbyatestsubjectashappeningataparticularinstantduringtherecording. Eventsaremostcommonlyassociated
withon-oroffsetofstimuluspresentations,orwiththedistinctmarkerofon-oroffsetofasubject’sresponseormotoraction. Othereventsmayincludeunplannedincidents
(for example, sudden onset of noise and vibrations due to construction work, laboratory device malfunction), changes in task instructions (for example, switching the
response hand), or experiment control parameters (for example, changing the stimulus presentation rate over experimental blocks), and noted data feature occurrences
(for example, a recording electrode producing noise). In BIDS, each event has an onset time and duration. Note that not all tasks will have recorded events (for example,
”resting state”).

## events (suffixes).

```
Name: Events
Type: Suffix
Format:<entities>_events.<extension>
```

Description: Event timing information from a behavioral task.

## extension (common_principles)

Name: File extension

Type: Common Principle

Description: A portion of the file name after the left-most period (.) preceded by any other alphanumeric. For example,.gitignoredoes not have a file extension, but
the file extension oftest.nii.gzis.nii.gz. Note that the left-most period is included in the file extension.

## fdt (extensions).

Name: EEGLAB FDT

Type: Extension

Format:<entities>_<suffix>.fdt

Description: AnEEGLABfile.The format used by the MATLAB toolboxEEGLAB. Each recording consists of a.setfile with an optional.fdtfile.

## fieldmap (suffixes)

Name: Fieldmap

Type: Suffix

Format:<entities>_fieldmap.<extension>

Description: Some MR schemes such as spiral-echo imaging (SEI) sequences are able to directly provide maps of the B0 field inhomogeneity.

## fif (extensions)

Name: Functional Imaging File Format

Type: Extension

Format:<entities>_<suffix>.fif

Description: An MEG file format used by Neuromag, Elekta, and MEGIN.


## file_relative (formats)

Name: Path relative to the parent file

Type: Format

Regular expression:(?!/)[0-9a-zA-Z/\_\-\.]+

Description: A path to a file, relative to the file in which the field is defined.The validation for this format is minimal. It simply ensures that the value is a string with any
characters that may appear in a valid path, without starting with ”/” (an absolute path).

## filename (columns).

Name: Filename

Type: Column

Description: Relative paths to files.

Schema information:

format **:** participant_relative
type **:** string

## flip (entities)

Name: Flip Angle

Type: Entity

Description: Iffilesbelongingtoanentity-linkedfilecollectionareacquiredatdifferentflipangles,the_flip-<index>entitypairMUSTbeusedtodistinguishindividual
files.Thisentityrepresentsthe"FlipAngle"metadatafield. Therefore,iftheflip-<index>entityispresentinafilename,"FlipAngle"MUSTbedefinedintheassociated
metadata. Please note that the<index>denotes the number/index (in the form of a nonnegative integer), not the"FlipAngle"value of the separate JSON file.

Schema information:

format **:** index
type **:** string

## fmap (datatypes).

Name: Field maps

Type: Datatype


Description: MRI scans for estimating B0 inhomogeneity-induced distortions.

## func (datatypes)

Name: Task-Based Magnetic Resonance Imaging

Type: Datatype

Description: Task (including resting state) imaging data

## genetic_info (files)

Name: Genetic Information

Type: Files And Directories

Description: The genetic_info.jsonfile describes the genetic information available in the participants.tsvfile and/or the genetic database described in
dataset_description.json. Datasets containing theGeneticsfield indataset_description.jsonor thegenetic_idcolumn inparticipants.tsvMUST in-
clude this file.

Schema information:

file_type **:** regular

## group sense 1 (columns)

Name: Channel group

Type: Column

Description: Which group of channels (grid/strip/seeg/depth) this channel belongs to. This is relevant because one group has one cable-bundle and noise can be shared.
This can be a name or number.

Schema information:

anyOf **:**

**-** type **:** string
**-** type **:** number

## handedness (columns)

Name: Subject handedness


Type: Column

Allowed values:left,l,L,LEFT,Left,right,r,R,RIGHT,Right,ambidextrous,a,A,AMBIDEXTROUS,Ambidextrous,n/a

Description: String value indicating one of ”left”, ”right”, ”ambidextrous”.For ”left”, use one of these values:left,l,L,LEFT,Left.For ”right”, use one of these values:
right,r,R,RIGHT,Right.For ”ambidextrous”, use one of these values:ambidextrous,a,A,AMBIDEXTROUS,Ambidextrous.

Schema information:

type **:** string

## headshape (suffixes)

Name: Headshape File

Type: Suffix

Format:<entities>_headshape.<extension>

Description: The 3-D locations of points that describe the head shape and/or electrode locations can be digitized and stored in separate files.

## hed_version (formats)

Name: HED Version

Type: Format

Regularexpression:^(?:[a-zA-Z]+:)?(?:[a-zA-Z]+_)?(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\ (?:-(?:(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?\
(?:\+(?:[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$

Description: The version string of the used HED schema.

## hemisphere (columns)

Name: Electrode hemisphere

Type: Column

Allowed values:L,R

Description: The hemisphere in which the electrode is placed.

Schema information:

type **:** string


## hemisphere (entities).

Name: Hemisphere

Type: Entity

Allowed values:L,R

Description: Thehemi-<label>entityindicateswhichhemibrainisdescribedbythefile. AllowedlabelvaluesforthisentityareLandR,fortheleftandrighthemibrains,
respectively.

Schema information:

format **:** label
type **:** string

## high_cutoff (columns)

Name: High cutoff

Type: Column

Description: Frequenciesusedforthelow-passfilterappliedtothechannelinHz. Ifnolow-passfilterapplied,usen/a. Notethathardwareanti-aliasinginA/Dconversion
of all MEG/EEG electronics applies a low-pass filter; specify its frequency here if applicable.

Schema information:

anyOf **:**

**-** minimum **:** 0
    type **:** number
    unit **:** Hz
**-** enum **:**
    **-** n/a
    type **:** string

## hplc_recovery_fractions (columns)

Name: HPLC recovery fractions

Type: Column

Description: HPLC recovery fractions (the fraction of activity that gets loaded onto the HPLC).

Schema information:


type **:** number
unit **:** arbitrary

## iEEGCoordinateProcessingDescription (metadata)

Name: iEEG Coordinate Processing Description

Type: Metadata

Description: Has any post-processing (such as projection) been done on the electrode positions (for example,"surface_projection","none").

Schema information:

type **:** string

## iEEGCoordinateProcessingReference (metadata)

Name: iEEG Coordinate Processing Reference

Type: Metadata

Description: A reference to a paper that defines in more detail the method used to localize the electrodes and to post-process the electrode positions.

Schema information:

type **:** string

## iEEGCoordinateSystem (metadata).

Name: iEEG Coordinate System

Type: Metadata

Allowedvalues:Pixels,ACPC,Other,ICBM452AirSpace,ICBM452Warp5Space,IXI549Space,fsaverage,fsaverageSym,fsLR,MNIColin27,MNI152Lin,MNI152NLin2009aSym,
MNI152NLin2009bSym,MNI152NLin2009cSym,MNI152NLin2009aAsym,MNI152NLin2009bAsym,MNI152NLin2009cAsym,MNI152NLin6Sym,MNI152NLin6ASym,MNI305,NIHPD,
OASIS30AntsOASISAnts,OASIS30Atropos,Talairach,UNCInfant,fsaverage3,fsaverage4,fsaverage5,fsaverage6,fsaveragesym,UNCInfant0V21,UNCInfant1V21,
UNCInfant2V21,UNCInfant0V22,UNCInfant1V22,UNCInfant2V22,UNCInfant0V23,UNCInfant1V23,UNCInfant2V23

Description: DefinesthecoordinatesystemfortheiEEGsensors. SeetheCoordinateSystemsAppendixforalistofrestrictedkeywordsforcoordinatesystems. If"Other",
provide definition of the coordinate system iniEEGCoordinateSystemDescription. If positions correspond to pixel indices in a 2D image (of either a volume-rendering,
surface-rendering, operative photo, or operative drawing), this MUST be"Pixels". For more information, see the section on Coordinate Systems Appendix.

Schema information:

type **:** string


## iEEGCoordinateSystemDescription (metadata)

Name: iEEG Coordinate System Description

Type: Metadata

Description: Free-form text description of the coordinate system. May also include a link to a documentation page or paper describing the system in greater detail.

Schema information:

type **:** string

## iEEGCoordinateUnits (metadata).

Name: iEEG Coordinate Units

Type: Metadata

Allowed values:m,mm,cm,pixels,n/a

Description: Units of the*_electrodes.tsv. MUST be"pixels"ifiEEGCoordinateSystemisPixels.

Schema information:

type **:** string

## iEEGElectrodeGroups (metadata)

Name: iEEG Electrode Groups

Type: Metadata

Description: Field to describe the way electrodes are grouped into strips, grids or depth probes. For example,"grid1: 10x8 grid on left temporal pole, strip2:
1x8 electrode strip on xxx".

Schema information:

type **:** string

## iEEGGround (metadata).

Name: iEEG Ground

Type: Metadata

Description: Description of the location of the ground electrode ("placed on right mastoid (M2)").


Schema information:

type **:** string

## iEEGPlacementScheme (metadata).

Name: iEEG Placement Scheme

Type: Metadata

Description: Freeform description of the placement of the iEEG electrodes. Left/right/bilateral/depth/surface (for example,"left frontal grid and bilateral
hippocampal depth"or"surface strip and STN depth"or"clinical indication bitemporal, bilateral temporal strips and left grid").

Schema information:

type **:** string

## iEEGReference (metadata)

Name: iEEG Reference

Type: Metadata

Description: General description of the reference scheme used and (when applicable) of location of the reference electrode in the raw recordings (for example,"left
mastoid","bipolar","T01"for electrode with name T01,"intracranial electrode on top of a grid, not included with data","upside down electrode").
If different channels have a different reference, this field should have a general description and the channel specific reference should be defined in thechannels.tsvfile.

Schema information:

type **:** string

## ieeg (datatypes).

Name: Intracranial electroencephalography

Type: Datatype

Description: Intracranial electroencephalography (iEEG) or electrocorticography (ECoG) data

## ieeg (modalities)

Name: Intracranial Electroencephalography

Type: Modalities


Description: Data acquired with iEEG.

## ieeg (suffixes)

Name: Intracranial Electroencephalography

Type: Suffix

Format:<entities>_ieeg.<extension>

Description: Intracranial electroencephalography recording data.

## impedance (columns).

Name: Electrode impedance

Type: Column

Description: Impedance of the electrode, units MUST be inkOhm.

Schema information:

type **:** number
unit **:** kOhm

## index (columns)

Name: Label index

Type: Column

Description: The label integer index.

Schema information:

type **:** integer

## index (common_principles)

Name: index

Type: Common Principle

Description: A nonnegative integer, possibly prefixed with arbitrary number of 0s for consistent indentation, for example, it is 01 inrun-01followingrun-<index>
specification.


## index (formats).

Name: Index

Type: Format

Regular expression:[0-9]*[1-9]+[0-9]*

Description: Non-negative, non-zero integers, optionally prefixed with leading zeros for sortability. An index may not be all zeros.

## inplaneT1 (suffixes)

Name: Inplane T1

Type: Suffix

Format:<entities>_inplaneT1.<extension>

Description: In arbitrary units (arbitrary). T1 weighted structural image matched to a functional (task) image.

Schema information:

unit **:** arbitrary

## inplaneT2 (suffixes)

Name: Inplane T2

Type: Suffix

Format:<entities>_inplaneT2.<extension>

Description: In arbitrary units (arbitrary). T2 weighted structural image matched to a functional (task) image.

Schema information:

unit **:** arbitrary

## integer (formats)

Name: Integer

Type: Format

Regular expression:[+-]?\d+

Description: An integer which may be positive or negative.


## inversion (entities)

Name: Inversion Time

Type: Entity

Description: If files belonging to an entity-linked file collection are acquired at different inversion times, theinv-<index>entity MUST be used to distinguish individual
files.This entity represents the"InversionTimemetadata field. Therefore, if theinv-<index>entity is present in a filename,"InversionTime"MUST be defined in the
associatedmetadata. Pleasenotethatthe<index>denotesthenumber/index(intheformofanonnegativeinteger),notthe"InversionTime"valueoftheseparateJSON
file.

Schema information:

format **:** index
type **:** string

## jpg (extensions).

Name: Joint Photographic Experts Group Format

Type: Extension

Format:<entities>_<suffix>.jpg

Description: A JPEG image file.

## json (extensions)

Name: JavaScript Object Notation

Type: Extension

Format:<entities>_<suffix>.json

Description: A JSON file.In the BIDS specification, JSON files are primarily used as ”sidecar” files, in which metadata describing ”data” files are encoded. These sidecar
files follow the inheritance principle.There are also a few special cases of JSON files being first-order data files, such asgenetic_info.json.

## kdf (extensions)

Name: KRISS KDF

Type: Extension

Format:<entities>_<suffix>.kdf


Description: AKRISS(filewithextension.kdf)file.EachexperimentalrunontheKRISSsystemproducesafilewithextension.kdf. Additionalfilesthatmaybeavailable
inthesamedirectoryincludethedigitizedpositionsoftheheadpoints(\_digitizer.txt),thepositionofthecenteroftheMEGcoils(.chn),andtheeventmarkers(.trg).

## label (common_principles).

Name: label

Type: Common Principle

Description: Analphanumericvalue,possiblyprefixedwitharbitrarynumberof0sforconsistentindentation,forexample,itisrestintask-restfollowingtask-<label>
specification. Note that labels MUST not collide when casing is ignored (see Case collision intolerance).

## label (entities).

Name: Label

Type: Entity

Description: Tissue-type label, following a prescribed vocabulary. Applies to binary masks and probabilistic/partial volume segmentations that describe a single tissue
type.This entity is only applicable to derivative data.

Schema information:

format **:** label
type **:** string

## label (formats)

Name: Label

Type: Format

Regular expression:[0-9a-zA-Z]+

Description: Freeform labels without special characters.

## labelgii (extensions)

Name: GIFTI label/annotation file

Type: Extension

Format:<entities>_<suffix>.label.gii


Description: A GIFTI label/annotation file.This extension may only be used in derivative datasets.

## low_cutoff (columns).

Name: Low cutoff

Type: Column

Description: Frequencies used for the high-pass filter applied to the channel in Hz. If no high-pass filter applied, usen/a.

Schema information:

anyOf **:**

**-** type **:** number
    unit **:** Hz
**-** enum **:**
    **-** n/a
    type **:** string

## m0scan (suffixes).

Name: M0 image

Type: Suffix

Format:<entities>_m0scan.<extension>

Description: The M0 image is a calibration image, used to estimate the equilibrium magnetization of blood.

## magnitude (suffixes)

Name: Magnitude

Type: Suffix

Format:<entities>_magnitude.<extension>

Description: Field-mappingMRschemessuchasgradient-recalledecho(GRE)generateaMagnitudeimagetobeusedforanatomicalreference. Requirestheexistenceof
Phase, Phase-difference or Fieldmap maps.

## magnitude1 (suffixes)

Name: Magnitude


Type: Suffix

Format:<entities>_magnitude1.<extension>

Description: Magnitude map generated by GRE or similar schemes, associated with the first echo in the sequence.

## magnitude2 (suffixes)

Name: Magnitude

Type: Suffix

Format:<entities>_magnitude2.<extension>

Description: Magnitude map generated by GRE or similar schemes, associated with the second echo in the sequence.

## manufacturer (columns).

Name: Manufacturer

Type: Column

Description: The manufacturer for each electrode. Can be used if electrodes were manufactured by more than one company.

Schema information:

type **:** string

## mapping (columns).

Name: Label mapping

Type: Column

Description: Corresponding integer label in the standard BIDS label lookup.

Schema information:

type **:** integer

## markers (suffixes).

Name: MEG Sensor Coil Positions

Type: Suffix


Format:<entities>_markers.<extension>

Description: Another manufacturer-specific detail pertains to the KIT/Yokogawa/Ricoh system, which saves the MEG sensor coil positions in a separate file with two
possible filename extensions (.sqd,.mrk). For these files, themarkerssuffix MUST be used. For example:sub-01_task-nback_markers.sqd

## mask (suffixes)

Name: Binary Mask

Type: Suffix

Format:<entities>_mask.<extension>

Description: A binary mask that functions as a discrete ”label” for a single structure.This suffix may only be used in derivative datasets.

## material (columns)

Name: Electrode material

Type: Column

Description: Material of the electrode (for example,Tin,Ag/AgCl,Gold).

Schema information:

type **:** string

## md (extensions).

Name: Markdown

Type: Extension

Format:<entities>_<suffix>.md

Description: A Markdown file.

## mefd (extensions)

Name: Multiscale Electrophysiology File Format Version 3.0

Type: Extension

Format:<entities>_<suffix>.mefd/


Description: A directory in theMEF3format.Each recording consists of a.mefddirectory.

## meg (datatypes)

Name: Magnetoencephalography

Type: Datatype

Description: Magnetoencephalography

## meg (modalities)

Name: Magnetoencephalography

Type: Modalities

Description: Data acquired with an MEG scanner.

## meg (suffixes).

Name: Magnetoencephalography

Type: Suffix

Format:<entities>_meg.<extension>

Description: Unprocessed MEG data stored in the native file format of the MEG instrument with which the data was collected.

## metabolite_parent_fraction (columns)

Name: Metabolite parent fraction

Type: Column

Description: Parent fraction of the radiotracer (0-1).

Schema information:

maximum **:** 1
minimum **:** 0
type **:** number


## metabolite_polar_fraction (columns).

Name: Metabolite polar fraction

Type: Column

Description: Polar metabolite fraction of the radiotracer (0-1).

Schema information:

maximum **:** 1
minimum **:** 0
type **:** number

## mhd (extensions).

Name: ITAB Binary Header

Type: Extension

Format:<entities>_<suffix>.mhd

Description: Produced by ITAB-ARGOS153 systems. This file a binary header file, and is generated along with a raw data file with the.rawextension.

## micr (datatypes)

Name: Microscopy

Type: Datatype

Description: Microscopy

## micr (modalities)

Name: Microscopy

Type: Modalities

Description: Data acquired with a microscope.

## modality (common_principles)

Name: Modality


Type: Common Principle

Description: The category of brain data recorded by a file. For MRI data, different pulse sequences are considered distinct modalities, such asT1w,boldordwi. For
passive recording techniques, such as EEG, MEG or iEEG, the technique is sufficiently uniform to define the modalitieseeg,megandieeg. When applicable, the modality
is indicated in the suffix. The modality may overlap with, but should not be confused with the data type.

## modality (entities)

Name: Corresponding Modality

Type: Entity

Description: Themod-<label>entity corresponds to modality label for defacing masks, for example, T1w, inplaneT1, referenced by a defacemask image. For example,
sub-01_mod-T1w_defacemask.nii.gz.

Schema information:

format **:** label
type **:** string

## mri (modalities).

Name: Magnetic Resonance Imaging

Type: Modalities

Description: Data acquired with an MRI scanner.

## mrk (extensions)

Name: MRK

Type: Extension

Format:<entities>_<suffix>.mrk

Description: A file containing MEG sensor coil positions.Used by KIT, Yokogawa, and Ricoh MEG systems. Successor to the.sqdextension for marker files.

## mtransfer (entities).

Name: Magnetization Transfer

Type: Entity


Allowed values:on,off

Description: If files belonging to an entity-linked file collection are acquired at different magnetization transfer (MT) states, the_mt-<label>entity MUST be used to
distinguish individual files.This entity represents the"MTState"metadata field. Therefore, if themt-<label>entity is present in a filename,"MTState"MUST be defined
in the associated metadata. Allowed label values for this entity areonandoff, for images acquired in presence and absence of an MT pulse, respectively.

Schema information:

format **:** label
type **:** string

## name sense 1 (columns)

Name: Channel name

Type: Column

Description: Label of the channel.

Schema information:

type **:** string

## name sense 2 (columns)

Name: Electrode name

Type: Column

Description: Name of the electrode contact point.

Schema information:

type **:** string

## name sense 3 (columns)

Name: Optode name

Type: Column

Description: Name of the optode, must be unique.

Schema information:

type **:** string


## name sense 4 (columns)

Name: Label name

Type: Column

Description: The unique label name.

Schema information:

type **:** string

## nii (extensions)

Name: NIfTI

Type: Extension

Format:<entities>_<suffix>.nii

Description: A Neuroimaging Informatics Technology Initiative (NIfTI) data file.

## niigz (extensions).

Name: Compressed NIfTI

Type: Extension

Format:<entities>_<suffix>.nii.gz

Description: A compressed Neuroimaging Informatics Technology Initiative (NIfTI) data file.

## nirs (datatypes).

Name: Near-Infrared Spectroscopy

Type: Datatype

Description: Near-Infrared Spectroscopy data organized around the SNIRF format

## nirs (modalities)

Name: Near-Infrared Spectroscopy


Type: Modalities

Description: Data acquired with NIRS.

## nirs (suffixes)

Name: Near Infrared Spectroscopy

Type: Suffix

Format:<entities>_nirs.<extension>

Description: Data associated with a Shared Near Infrared Spectroscopy Format file.

## notch (columns)

Name: Notch frequencies

Type: Column

Description: Frequencies used for the notch filter applied to the channel, in Hz. If no notch filter applied, usen/a.

Schema information:

anyOf **:**

**-** type **:** number
    unit **:** Hz
**-** enum **:**
    **-** n/a
    type **:** string

## number (formats)

Name: Number

Type: Format

Regular expression:[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)([eE][+-]?[0-9]+)?

Description: A number which may be an integer or float, positive or negative.


## nwb (extensions)

Name: Neurodata Without Borders Format

Type: Extension

Format:<entities>_<suffix>.nwb

Description: ANeurodata Without Bordersfile.Each recording consists of a single.nwbfile.

## onset (columns).

Name: Event onset

Type: Column

Description: Onset (in seconds) of the event, measured from the beginning of the acquisition of the first data point stored in the corresponding task data file. Negative
onsets are allowed, to account for events that occur prior to the first stored data point. For example, in case there is an in-scanner training phase that begins before the
scanningsequencehasstartedeventsfromthissequenceshouldhavenegativeonsettimecountingdowntothebeginningoftheacquisitionofthefirstvolume.Ifanydata
pointshavebeendiscardedbeforeformingthedatafile(forexample, ”dummyvolumes”inBOLDfMRI),atimeof0correspondstothefirststoreddatapointandnotthe
first acquired data point.

Schema information:

type **:** number
unit **:** s

## optodes (suffixes).

Name: Optodes

Type: Suffix

Format:<entities>_optodes.<extension>

Description: Either a light emitting device, sometimes called a transmitter, or a photoelectric transducer, sometimes called a receiver.

## orientation_component (columns)

Name: Orientation Component

Type: Column

Allowed values:x,y,z


Description: Description of the orientation of the channel.

Schema information:

type **:** string

## part (entities)

Name: Part

Type: Entity

Allowed values:mag,phase,real,imag

Description: This entity is used to indicate which component of the complex representation of the MRI signal is represented in voxel data. Thepart-<label>entity is
associated with the DICOM Tag0008, 9208. Allowed label values for this entity arephase,mag,realandimag, which are typically used inpart-mag/part-phaseor
part-real/part-imagpairs of files.Phase images MAY be in radians or in arbitrary units. The sidecar JSON file MUST include the units of thephaseimage. The possible
options are"rad"or"arbitrary".When there is only a magnitude image of a given type, thepartentity MAY be omitted.

Schema information:

format **:** label
type **:** string

## participant_id (columns).

Name: Participant ID

Type: Column

Description: A participant identifier of the formsub-<label>, matching a participant entity found in the dataset.

Schema information:

type **:** string

## participant_relative (formats).

Name: Path relative to the participant directory

Type: Format

Regular expression:(?!/)(?!sub-)[0-9a-zA-Z/\_\-\.]+


```
Description: Apathtoafile,relativetotheparticipant’sdirectoryinthedataset.Thevalidationforthisformatisminimal. Itsimplyensuresthatthevalueisastringwith
any characters that may appear in a valid path, without starting with ”/” (an absolute path) or ”sub/” (a relative path starting with the participant directory, rather than
relative to that directory).
```
## participants (files)

Name: Participant Information
Type: Files And Directories
Description: ThepurposeofthisRECOMMENDEDfileistodescribepropertiesofparticipantssuchasage, sex, handedness. Ifthisfileexists, itMUSTcontainthecolumn
participant_id,whichMUSTconsistofsub-<label>valuesidentifyingonerowforeachparticipant,followedbyalistofoptionalcolumnsdescribingparticipants. Each
participant MUST be described by one and only one row.Commonly used optional columns inparticipant.tsvfiles areage,sex, andhandedness. We RECOMMEND
to make use of these columns, and in case that you do use them, we RECOMMEND to use the following values for them:-age: numeric value in years (float or integer
value)-sex: string value indicating phenotypical sex, one of ”male”, ”female”, ”other” - for ”male”, use one of these values:male,m,M,MALE,Male- for ”female”, use one
of these values:female,f,F,FEMALE,Female- for ”other”, use one of these values:other,o,O,OTHER,Other-handedness: string value indicating one of ”left”, ”right”,
”ambidextrous” - for ”left”, use one of these values:left,l,L,LEFT,Left- for ”right”, use one of these values:right,r,R,RIGHT,Right- for ”ambidextrous”, use one of
these values:ambidextrous,a,A,AMBIDEXTROUS,AmbidextrousThroughout BIDS you can indicate missing values withn/a(for ”not available”).
Schema information:
file_type **:** regular

## pathology (columns).

```
Name: Pathology
Type: Column
Description: String value describing the pathology of the sample or type of control. When different fromhealthy, pathology SHOULD be specified. The pathology may
be specified in eithersamples.tsvorsessions.tsv, depending on whether the pathology changes over time.
Schema information:
type : string
```
## perf (datatypes)

```
Name: Perfusion imaging
Type: Datatype
Description: Blood perfusion imaging data, including arterial spin labeling (ASL)
```

## pet (datatypes)

Name: Positron Emission Tomography

Type: Datatype

Description: Positron emission tomography data

## pet (modalities).

Name: Positron Emission Tomography

Type: Modalities

Description: Data acquired with PET.

## pet (suffixes)

Name: Positron Emission Tomography

Type: Suffix

Format:<entities>_pet.<extension>

Description: PETimagingdataSHOULDbestoredin4D(or3D,ifonlyonevolumewasacquired)NIfTIfileswiththe_petsuffix. VolumesMUSTbestoredinchronological
order (the order they were acquired in).

### phase (suffixes)

Name: Phase image

Type: Suffix

Format:<entities>_phase.<extension>

Description: DEPRECATED. Phase information associated with magnitude information stored in BOLD contrast. This suffix should be replaced by the DEPRECATED
in conjunction with theboldsuffix.

Schema information:

anyOf **:**

**-** unit **:** arbitrary
**-** unit **:** rad


### phase1 (suffixes)

Name: Phase

Type: Suffix

Format:<entities>_phase1.<extension>

Description: Phase map generated by GRE or similar schemes, associated with the first echo in the sequence.

### phase2 (suffixes)

Name: Phase

Type: Suffix

Format:<entities>_phase2.<extension>

Description: Phase map generated by GRE or similar schemes, associated with the second echo in the sequence.

### phasediff (suffixes)

Name: Phase-difference

Type: Suffix

Format:<entities>_phasediff.<extension>

Description: Somescannerssubtractthephase1fromthephase2mapandgenerateauniquephasedifffile. Forinstance,thisisacommonoutputforthebuilt-infieldmap
sequence of Siemens scanners.

### photo (suffixes)

Name: Photo File

Type: Suffix

Format:<entities>_photo.<extension>

Description: Photos of the anatomical landmarks, head localization coils or tissue sample.

### physio (suffixes)

Name: Physiological recording


Type: Suffix

Format:<entities>_physio.<extension>

Description: Physiological recordings such as cardiac and respiratory signals.

### plasma_radioactivity (columns)

Name: Plasma radioactivity

Type: Column

Description: Radioactivity in plasma, in unit of plasma radioactivity (for example,kBq/mL).

Schema information:

type **:** number

### png (extensions)

Name: Portable Network Graphics

Type: Extension

Format:<entities>_<suffix>.png

Description: APortable Network Graphicsfile.

### pos (extensions)

Name: Head Point Position

Type: Extension

Format:<entities>_<suffix>.pos

Description: File containing digitized positions of the head points.This may be produced by a 4D neuroimaging/BTi MEG system or a CTF MEG system.

### probseg (suffixes)

Name: Probabilistic Segmentation

Type: Suffix

Format:<entities>_probseg.<extension>


Description: A probabilistic segmentation.This suffix may only be used in derivative datasets.

### processing (entities)

Name: Processed (on device)

Type: Entity

Description: The proc label is analogous to rec for MR and denotes a variant of a file that was a result of particular processing performed on the device.This is useful for
files produced in particular by Elekta’s MaxFilter (for example,sss,tsss,trans,quatormc), which some installations impose to be run on raw data because of active
shielding software corrections before the MEG data can actually be exploited.

Schema information:

format **:** label
type **:** string

### raw (extensions)

Name: RAW

Type: Extension

Format:<entities>_<suffix>.raw

Description: When produced by a KIT / Yokogawa / Ricoh MEG system, this file contains trial-based evoked fields.When produced by an ITAB-ARGOS153 system, this
file contains raw data and is generated along with an associated binary header file with the.mhdextension.

### reconstruction (entities)

Name: Reconstruction

Type: Entity

Description: Therec-<label>entity can be used to distinguish different reconstruction algorithms (for example,MoCofor the ones using motion correction).

Schema information:

format **:** label
type **:** string


### recording (entities)

Name: Recording

Type: Entity

Description: Therecording-<label>entitycanbeusedtodistinguishcontinuousrecordingfiles.Thisentityiscommonlyappliedwhencontinuousrecordingshavediffer-
entsamplingfrequenciesorstarttimes. Forexample,physiologicalrecordingswithdifferentsamplingfrequenciesmaybedistinguishedusinglabelslikerecording-100Hz
andrecording-500Hz.

Schema information:

format **:** label
type **:** string

### reference sense 1 (columns)

Name: Electrode reference

Type: Column

Description: Name of the reference electrode(s). This column is not needed when it is common to all channels. In that case the reference electrode(s) can be specified in
*_eeg.jsonasEEGReference).

Schema information:

type **:** string

### reference sense 2 (columns)

Name: Electrode reference

Type: Column

Description: Specification of the reference (for example,mastoid,ElectrodeName01,intracranial,CAR,other,n/a). If the channel is not an electrode channel (for
example, a microphone channel) usen/a.

Schema information:

anyOf **:**

**-** type **:** string
**-** enum **:**
    **-** n/a
    type **:** string


### resolution (entities)

Name: Resolution

Type: Entity

Description: ResolutionofregularlysampledN-dimensionaldata.Thisentityrepresentsthe"Resolution"metadatafield. Therefore,iftheres-<label>entityispresent
in a filename,"Resolution"MUST also be added in the JSON file, to provide interpretation.This entity is only applicable to derivative data.

Schema information:

format **:** label
type **:** string

### respiratory (columns)

Name: Respiratory measurement

Type: Column

Description: continuous breathing measurement

Schema information:

type **:** number

### response_time (columns)

Name: Response time

Type: Column

Description: Response time measured in seconds. A negative response time can be used to represent preemptive responses andn/adenotes a missed response.

Schema information:

anyOf **:**

**-** type **:** number
    unit **:** s
**-** enum **:**
    **-** n/a
    type **:** string


### rrid (formats)

Name: Research resource identifier

Type: Format

Regular expression:RRID:.+_.+

Description: Aresearch resource identifier.

### rst (extensions)

Name: reStructuredText

Type: Extension

Format:<entities>_<suffix>.rst

Description: AreStructuredTextfile.

### run (common_principles)

Name: Run

Type: Common Principle

Description: An uninterrupted repetition of data acquisition that has the same acquisition parameters and task (however events can change from run to run due to
differentsubjectresponseorrandomizednatureofthestimuli). Runisasynonymofadataacquisition. Notethat”uninterrupted”maylookdifferentbymodalitydueto
the nature of the recording. For example, in MRI or MRI, if a subject leaves the scanner, the acquisition must be restarted. For some types of MRI acquisitions, a subject
may leave and re-enter the scanner without interrupting the scan.

### run (entities)

Name: Run

Type: Entity

Description: Therun-<index>entity is used to distinguish separate data acquisitions with the same acquisition parameters and (other) entities.If several data acquisi-
tions (for example, MRI scans or EEG recordings) with the same acquisition parameters are acquired in the same session, they MUST be indexed with therun-<index>
entity:_run-1,_run-2,_run-3, and so on (only nonnegative integers are allowed as run indices).If different entities apply, such as a different session indicated by
[ses-<label>][../appendices/entities.md#ses), or different acquisition parameters indicated byrun-<index>, thenrunis not needed to distinguish the scans and MAY be
omitted.

Schema information:


```
format : index
type : string
```
### sample (columns)

Name: Sample index
Type: Column
Description: Onset of the event according to the sampling scheme of the recorded modality (that is, referring to the raw data file that theevents.tsvfile accompanies).
When there are several sampling schemes present in the raw data file (as can be the case for example for.edffiles), this column is ambiguous and SHOULD NOT be used.

```
Schema information:
type : integer
```
### sample (common_principles)

```
Name: Sample
Type: Common Principle
Description: A sample pertaining to a subject such as tissue, primary cell or cell-free sample. Sample labels MUST be unique within a subject and it is RECOMMENDED
that they be unique throughout the dataset.
```
### sample (entities)

```
Name: Sample
Type: Entity
Description: A sample pertaining to a subject such as tissue, primary cell or cell-free sample. Thesample-<label>entity is used to distinguish between different samples
from the same subject. The label MUST be unique per subject and is RECOMMENDED to be unique throughout the dataset.
Schema information:
format : label
type : string
```
### sample_id (columns)

```
Name: Sample ID
```

Type: Column

Description: A sample identifier of the formsample-<label>, matching a sample entity found in the dataset.

Schema information:

type **:** string

### sample_type (columns)

Name: Sample type

Type: Column

Allowed values:cell line,in vitro differentiated cells,primary cell,cell-free sample,cloning host,tissue,whole organisms,organoid,technical
sample

Description: Biosample type defined byENCODE Biosample Type.

Schema information:

type **:** string

### samples (files)

Name: Sample Information

Type: Files And Directories

Description: The purpose of this file is to describe properties of samples, indicated by thesampleentity. This file is REQUIRED ifsample-<label>is present in any file
name within the dataset. If this file exists, it MUST contain the three following columns:-sample_id: MUST consist ofsample-<label>values identifying one row for
each sample-participant_id: MUST consist ofsub-<label>-sample_type: MUST consist of sample type values, eithercell line,in vitro differentiated cells,
primary cell,cell-free sample,cloning host,tissue,whole organisms,organoidortechnical samplefromENCODE Biosample TypeOther optional columns
MAYbeusedtodescribethesamples. EachsampleMUSTbedescribedbyoneandonlyonerow.Commonlyusedoptionalcolumnsinsamples.tsvfilesarepathologyand
derived_from. We RECOMMEND to make use of these columns, and in case that you do use them, we RECOMMEND to use the following values for them:-pathology:
string value describing the pathology of the sample or type of control. When different fromhealthy, pathology SHOULD be specified insamples.tsv. The pathology
MAY instead be specified in Sessions files in case it changes over time.-derived_from:sample-<label>key/value pair from which a sample is derived from, for example
a slice of tissue (sample-02) derived from a block of tissue (sample-01)

Schema information:

file_type **:** regular


### sampling_frequency (columns)

Name: Channel sampling frequency

Type: Column

Description: Sampling rate of the channel in Hz.

Schema information:

type **:** number
unit **:** Hz

### sbref (suffixes)

Name: Single-band reference image

Type: Suffix

Format:<entities>_sbref.<extension>

Description: Single-band reference for one or more multi-banddwiimages.

### scans (suffixes)

Name: Scans file

Type: Suffix

Format:<entities>_scans.<extension>

Description: Thepurposeofthisfileistodescribetimingandotherpropertiesofeachimagingacquisitionsequence(eachrunfile)withinonesession. Eachneuralrecording
file SHOULD be described by exactly one row. Some recordings consist of multiple parts, that span several files, for example through echo-, part-, or split- entities. Such
recordings MUST be documented with one row per file. Relative paths to files should be used under a compulsory filename header. If acquisition time is included it
should be listed under the acq_time header. Acquisition time refers to when the first data point in each run was acquired. Furthermore, if this header is provided, the
acquisition times of all files that belong to a recording MUST be identical. Datetime should be expressed as described in Units. Additional fields can include external
behavioral measures relevant to the scan. For example vigilance questionnaire score administered after a resting state scan. All such included additional fields SHOULD
be documented in an accompanying _scans.json file that describes these fields in detail (see Tabular files).

### session (common_principles)

Name: Session

Type: Common Principle


Description: Alogicalgroupingofneuroimagingandbehavioraldataconsistentacrosssubjects. Sessioncan(butdoesn’thaveto)besynonymoustoavisitinalongitudinal
study. In general, subjects will stay in the scanner during one session. However, for example, if a subject has to leave the scanner room and then be re-positioned on the
scanner bed, the set of MRI acquisitions will still be considered as a session and match sessions acquired in other subjects. Similarly, in situations where different data
types are obtained over several visits (for example fMRI on one day followed by DWI the day after) those can be grouped in one session. Defining multiple sessions is
appropriatewhenseveralidenticalorsimilardataacquisitionsareplannedandperformedonall-ormost-subjects,ofteninthecaseofsomeinterventionbetweensessions
(for example, training). In the PET context, a session may also indicate a group of related scans, taken in one or more visits.

### session (entities)

Name: Session

Type: Entity

Description: Alogicalgroupingofneuroimagingandbehavioraldataconsistentacrosssubjects. Sessioncan(butdoesn’thaveto)besynonymoustoavisitinalongitudinal
study. In general, subjects will stay in the scanner during one session. However, for example, if a subject has to leave the scanner room and then be re-positioned on the
scannerbed,thesetofMRIacquisitionswillstillbeconsideredasasessionandmatchsessionsacquiredinothersubjects. Similarly,insituationswheredifferentdatatypes
areobtainedoverseveralvisits(forexamplefMRIononedayfollowedbyDWIthedayafter)thosecanbegroupedinonesession.Definingmultiplesessionsisappropriate
whenseveralidenticalorsimilardataacquisitionsareplannedandperformedonall-ormost-subjects,ofteninthecaseofsomeinterventionbetweensessions(forexample,
training).

Schema information:

format **:** label
type **:** string

### session_id (columns)

Name: Session ID

Type: Column

Description: A session identifier of the formses-<label>, matching a session found in the dataset.

Schema information:

type **:** string

### sessions (suffixes)

Name: Sessions file

Type: Suffix

Format:<entities>_sessions.<extension>


Description: In case of multiple sessions there is an option of adding additional sessions.tsv files describing variables changing between sessions. In such case one file per
participantSHOULDbeadded. ThesefilesMUSTincludeasession_idcolumnanddescribeeachsessionbyoneandonlyonerow. Columnnamesinsessions.tsvfilesMUST
be different from group level participant key column names in the participants.tsv file.

### set (extensions)

Name: EEGLAB SET

Type: Extension

Format:<entities>_<suffix>.set

Description: AnEEGLABfile.The format used by the MATLAB toolboxEEGLAB. Each recording consists of a.setfile with an optional.fdtfile.

### sex (columns)

Name: Sex

Type: Column

Allowed values:male,m,M,MALE,Male,female,f,F,FEMALE,Female,other,o,O,OTHER,Other,n/a

Description: String value indicating phenotypical sex, one of ”male”, ”female”, ”other”.For ”male”, use one of these values:male,m,M,MALE,Male.For ”female”, use one
of these values:female,f,F,FEMALE,Female.For ”other”, use one of these values:other,o,O,OTHER,Other.

Schema information:

type **:** string

### short_channel (columns)

Name: Short Channel

Type: Column

Description: Is the channel designated as short. The total number of channels listed as short channels SHOULD be stored inShortChannelCountin*_nirs.json.

Schema information:

type **:** boolean


### size (columns)

Name: Electrode size

Type: Column

Description: Surface area of the electrode, units MUST be inmm^2.

Schema information:

type **:** number
unit **:** mm^2

### snirf (extensions)

Name: Shared Near Infrared Spectroscopy Format

Type: Extension

Format:<entities>_<suffix>.snirf

Description: HDF5 file organized according to theSNIRF specification

### software_filters (columns)

Name: Software filters

Type: Column

Description: Listoftemporaland/orspatialsoftwarefiltersapplied(forexample,SSS,SpatialCompensation). NotethatparametersshouldbedefinedinthegeneralMEG
sidecar .json file. Indicaten/ain the absence of software filters applied.

Schema information:

anyOf **:**

**-** type **:** string
**-** enum **:**
    **-** n/a
    type **:** string

### source sense 1 (columns)

Name: Source name

Type: Column


Description: Name of the source as specified in the*_optodes.tsvfile.n/afor channels that do not contain fNIRS signals (for example, acceleration).

Schema information:

anyOf **:**

**-** type **:** string
**-** enum **:**
    **-** n/a
    type **:** string

### source sense 2 (columns)

Name: Source type

Type: Column

Description: The type of source. Only to be used if the fieldSourceTypein*_nirs.jsonis set tomixed.

Schema information:

anyOf **:**

**-** type **:** string

### sourcedata (files)

Name: Source data

Type: Files And Directories

Description: A directory where to store data before harmonization, reconstruction, and/or file format conversion (for example, E-Prime event logs or DICOM files). See
the relevant section for more information.

Schema information:

file_type **:** directory

### space (entities)

Name: Space

Type: Entity

Description: Thespace-<label>entity can be used to indicate the way in which electrode positions are interpreted (for EEG/MEG/iEEG data) or the spatial reference
to which a file has been aligned (for MRI data). The<label>MUST be taken from one of the modality specific lists in the Coordinate Systems Appendix. For example,


for iEEG data, the restricted keywords listed under Coordinate Systems Appendix are acceptable for<label>.For EEG/MEG/iEEG data, this entity can be applied to raw
data, but for other data types, it is restricted to derivative data.

Schema information:

format **:** label
type **:** string

### species (columns)

Name: Species

Type: Column

Description: ThespeciescolumnSHOULDbeabinomialspeciesnamefromtheNCBITaxonomy(forexample,homo sapiens,mus musculus,rattus norvegicus). For
backwards compatibility, ifspeciesis absent, the participant is assumed to behomo sapiens.

Schema information:

type **:** string

### split (entities)

Name: Split

Type: Entity

Description: Inthecaseoflongdatarecordingsthatexceedafilesizeof2Gb,.fiffilesareconventionallysplitintomultipleparts. Eachofthesefileshasaninternalpointer
tothenextfile. ThisisimportantwhenrenamingthesesplitrecordingstotheBIDSconvention.Insteadofasimplerenaming, filesshouldbereadinandsavedundertheir
newnameswithdedicatedtoolslikeMNE-Python,whichwillensurethatnotonlythefilenames,butalsotheinternalfilepointers,willbeupdated.ItisRECOMMENDED
that.fiffiles with multiple parts use thesplit-<index>entity to indicate each part. If there are multiple parts of a recording and the optionalscans.tsvis provided,
all files MUST be listed separately inscans.tsvand the entries for theacq_timecolumn inscans.tsvMUST all be identical, as described in Scans file.

Schema information:

format **:** index
type **:** string

### sqd (extensions)

Name: SQD

Type: Extension


Format:<entities>_<suffix>.sqd

Description: A file containing either raw MEG data or MEG sensor coil positions. While this extension is still valid, it has been succeeded by.confor raw MEG data and
.mrkfor marker information.Used by KIT, Yokogawa, and Ricoh MEG systems.

### stain (entities)

Name: Stain

Type: Entity

Description: Thestain-<label>key/pair values can be used to distinguish image files from the same sample using different stains or antibodies for contrast enhance-
ment.This entity represents the"SampleStaining"metadata field. Therefore, if thestain-<label>entity is present in a filename,"SampleStaining"SHOULD be
defined in the associated metadata, although the label may be different.Descriptions of antibodies SHOULD also be indicated in the"SamplePrimaryAntibodies"and/or
"SampleSecondaryAntobodies"metadata fields, as appropriate.

Schema information:

format **:** label
type **:** string

### status (columns)

Name: Channel status

Type: Column

Allowed values:good,bad,n/a

Description: Data quality observed on the channel. A channel is consideredbadif its data quality is compromised by excessive noise. If quality is unknown, then a value
ofn/amay be used. Description of noise type SHOULD be provided in[status_description].

Schema information:

type **:** string

### status_description (columns)

Name: Channel status description

Type: Column

Description: Freeform text description of noise or artifact affecting data quality on the channel. It is meant to explain why the channel was declared bad in thestatus
column.


Schema information:

type **:** string

### stim (suffixes)

Name: Continuous recording

Type: Suffix

Format:<entities>_stim.<extension>

Description: Continuous measures, such as parameters of a film or audio stimulus.

### stim_file (columns)

Name: Stimulus file

Type: Column

Description: Represents the location of the stimulus file (such as an image, video, or audio file) presented at the given onset time. There are no restrictions on the file
formats of the stimuli files, but they should be stored in the/stimulidirectory (under the root directory of the dataset; with optional subdirectories). The values under
thestim_filecolumn correspond to a path relative to/stimuli. For exampleimages/cat03.jpgwill be translated to/stimuli/images/cat03.jpg.

Schema information:

format **:** stimuli_relative
type **:** string

### stimuli (files)

Name: Stimulus files

Type: Files And Directories

Description: A directory to store any stimulus files used during an experiment. See the relevant section for more information.

Schema information:

file_type **:** directory


### stimuli_relative (formats)

Name: Path relative to the stimuli directory

Type: Format

Regular expression:(?!/)(?!stimuli/)[0-9a-zA-Z/\_\-\.]+

Description: A path to a stimulus file, relative to a/stimulidirectory somewhere.The validation for this format is minimal. It simply ensures that the value is a string
with any characters that may appear in a valid path, without starting with ”/” (an absolute path) or ”stimuli/” (a relative path starting with the stimuli directory, rather
than relative to that directory).

### strain (columns)

Name: Strain

Type: Column

Description: For species different fromhomo sapiens, string value indicating the strain of the species, for example:C57BL/6J.

Schema information:

type **:** string

### strain_rrid (columns)

Name: Strain RRID

Type: Column

Description: For species different fromhomo sapiens, research resource identifier (RRID) of the strain of the species, for example:RRID:IMSR_JAX:000664.

Schema information:

format **:** rrid
type **:** string

### string (formats)

Name: String

Type: Format

Regular expression:.*

Description: The basic string type (not a specific format). This should allow any free-form string.


### subject (common_principles)

Name: Subject

Type: Common Principle

Description: A person or animal participating in the study. Used interchangeably with term Participant.

### subject (entities)

Name: Subject

Type: Entity

Description: A person or animal participating in the study.

Schema information:

format **:** label
type **:** string

### suffix (common_principles)

Name: suffix

Type: Common Principle

Description: An alphanumeric string that forms part of a filename, located after all entities and following a final_, right before the file extension; for example, it iseegin
sub-05_task-matchingpennies_eeg.vhdr.

### task (common_principles)

Name: Task

Type: Common Principle

Description: Asetofstructuredactivitiesperformedbytheparticipant. Tasksareusuallyaccompaniedbystimuliandresponses,andcangreatlyvaryincomplexity. For
the purpose of this specification we consider the so-called ”resting state” a task. In the context of brain scanning, a task is always tied to one data acquisition. Therefore,
even if during one acquisition the subject performed multiple conceptually different behaviors (with different sets of instructions) they will be considered one (combined)
task.


### task (entities)

Name: Task

Type: Entity

Description: A set of structured activities performed by the participant. Tasks are usually accompanied by stimuli and responses, and can greatly vary in complexity.In
thecontextofbrainscanning,ataskisalwaystiedtoonedataacquisition. Therefore,evenifduringoneacquisitionthesubjectperformedmultipleconceptuallydifferent
behaviors(withdifferentsetsofinstructions)theywillbeconsideredone(combined)task.Whiletasksmayberepeatedacrossmultipleacquisitions,agiventaskmayhave
differentsetsofstimuli(forexample,randomizedorder)andparticipantresponsesacrosssubjects,sessions,andruns.Thetask-<label>MUSTbeconsistentacrosssubjects
and sessions.Files with thetask-<label>entity SHOULD have an associated events file, as well as certain metadata fields in the associated JSON file.For the purpose of
this specification we consider the so-called ”resting state” a task, although events files are not expected for resting state data. Additionally, a common convention in the
specification is to include the word ”rest” in thetasklabel for resting state files (for example,task-rest).

Schema information:

format **:** label
type **:** string

### template_x (columns)

Name: X template position

Type: Column

Description: Assumed or ideal position along the x axis.

Schema information:

anyOf **:**

**-** type **:** number
**-** enum **:**
    **-** n/a
    type **:** string

### template_y (columns)

Name: Y template position

Type: Column

Description: Assumed or ideal position along the y axis.

Schema information:


anyOf **:**

**-** type **:** number
**-** enum **:**
    **-** n/a
    type **:** string

### template_z (columns)

Name: Z template position

Type: Column

Description: Assumed or ideal position along the z axis.

Schema information:

anyOf **:**

**-** type **:** number
**-** enum **:**
    **-** n/a
    type **:** string

### tif (extensions)

Name: Tag Image File Format

Type: Extension

Format:<entities>_<suffix>.tif

Description: ATag Image File Formatfile.

### time (columns)

Name: Time

Type: Column

Description: Time, in seconds, relative toTimeZerodefined by the*_pet.json. For example, 5.

Schema information:

type **:** number
unit **:** s


### time (formats)

Name: Time

Type: Format

Regular expression:(?:2[0-3]|[01]?[0-9]):[0-5][0-9]:[0-5][0-9]

Description: A time in the form"hh:mm:ss".

### tracer (entities)

Name: Tracer

Type: Entity

Description: Thetrc-<label>entity can be used to distinguish sequences using different tracers.This entity represents the"TracerName"metadata field. Therefore, if
thetrc-<label>entity is present in a filename,"TracerName"MUST be defined in the associated metadata. Please note that the<label>does not need to match the
actual value of the field.

Schema information:

format **:** label
type **:** string

### trg (extensions)

Name: KRISS TRG

Type: Extension

Format:<entities>_<suffix>.trg

Description: A file generated by KRISS MEG systems containing the event markers.Each experimental run on the KRISS system produces a file with extension.kdf.
Additional files that may be available in the same directory include the digitized positions of the head points (\_digitizer.txt), the position of the center of the MEG
coils (.chn), and the event markers (.trg).

### trial_type (columns)

Name: Trial type

Type: Column

Description: Primary categorisation of each trial to identify them as instances of the experimental conditions. For example: for a response inhibition task, it could take
on valuesgoandno-goto refer to response initiation and response inhibition experimental conditions.


Schema information:

type **:** string

### trigger (columns)

Name: Trigger

Type: Column

Description: continuous measurement of the scanner trigger signal

Schema information:

type **:** number

### tsv (extensions)

Name: Tab-Delimited

Type: Extension

Format:<entities>_<suffix>.tsv

Description: A tab-delimited file.

### tsvgz (extensions)

Name: Compressed Tab-Delimited

Type: Extension

Format:<entities>_<suffix>.tsv.gz

Description: Agzippedtab-delimitedfile. Thisfileextensionisonlyusedforverylargetabulardata,suchasphysiologicalrecordings. Forsmallerdata,theunzipped.tsv
extension is preferred.

### txt (extensions)

Name: Text

Type: Extension

Format:<entities>_<suffix>.txt


Description: A free-form text file.Tab-delimited files should have the.tsvextension rather than a.txtextension.

### type sense 1 (columns)

Name: Channel type

Type: Column

Allowed values:AUDIO,EEG,EOG,ECG,EMG,EYEGAZE,GSR,HEOG,MISC,PPG,PUPIL,REF,RESP,SYSCLOCK,TEMP,TRIG,VEOG

Description: Type of channel; MUST use the channel types listed below. Note that the type MUST be in upper-case.

Schema information:

type **:** string

### type sense 2 (columns)

Name: Channel type

Type: Column

Allowed values:MEGMAG,MEGGRADAXIAL,MEGGRADPLANAR,MEGREFMAG,MEGREFGRADAXIAL,MEGREFGRADPLANAR,MEGOTHER,EEG,ECOG,SEEG,DBS,VEOG,HEOG,EOG,ECG,EMG,
TRIG,AUDIO,PD,EYEGAZE,PUPIL,MISC,SYSCLOCK,ADC,DAC,HLU,FITERR,OTHER

Description: Type of channel; MUST use the channel types listed below. Note that the type MUST be in upper-case.

Schema information:

type **:** string

### type sense 3 (columns)

Name: Channel type

Type: Column

Allowed values:EEG,ECOG,SEEG,DBS,VEOG,HEOG,EOG,ECG,EMG,TRIG,AUDIO,PD,EYEGAZE,PUPIL,MISC,SYSCLOCK,ADC,DAC,REF,OTHER

Description: Type of channel; MUST use the channel types listed below. Note that the type MUST be in upper-case.

Schema information:

type **:** string


### type sense 4 (columns)

Name: Channel type

Type: Column

Allowedvalues:NIRSCWAMPLITUDE,NIRSCWFLUORESCENSEAMPLITUDE,NIRSCWOPTICALDENSITY,NIRSCWHBO,NIRSCWHBR,NIRSCWMUA,MEGMAG,MEGGRADAXIAL,MEGGRADPLANAR,
MEGREFMAG,MEGREFGRADAXIAL,MEGREFGRADPLANAR,MEGOTHER,EEG,ECOG,SEEG,DBS,VEOG,HEOG,EOG,ECG,EMG,TRIG,AUDIO,PD,EYEGAZE,PUPIL,MISC,SYSCLOCK,ADC,DAC,
HLU,FITERR,ACCEL,GYRO,MAGN,MISC,OTHER

Description: Type of channel; MUST use the channel types listed below. Note that the type MUST be in upper-case.

Schema information:

type **:** string

### type sense 5 (columns)

Name: Electrode type

Type: Column

Description: Type of the electrode (for example, cup, ring, clip-on, wire, needle).

Schema information:

type **:** string

### type sense 6 (columns)

Name: Type

Type: Column

Allowed values:source,detector,n/a

Description: The type of the optode.

Schema information:

type **:** string

### uCT (suffixes)

Name: Micro-CT


Type: Suffix

Format:<entities>_uCT.<extension>

Description: Micro-CT imaging data

### unit (formats)

Name: A standardized unit

Type: Format

Regular expression:.*

Description: A unit. SI units in CMIXF formatting are RECOMMENDED (see Units).Currently this matches any string.TODO: Somehow reference the actual unit options
in the Units appendix.

### units sense 1 (columns)

Name: Units

Type: Column

Description: Physical unit of the value represented in this channel, for example,Vfor Volt, orfT/cmfor femto Tesla per centimeter (see Units).

Schema information:

format **:** unit
type **:** string

### units sense 2 (columns)

Name: Units

Type: Column

Description: Physicalunitofthevaluerepresentedinthischannel,specifiedaccordingtotheSIunitsymbolandpossiblyprefixsymbol,orasaderivedSIunit(forexample,
V, or unitless for changes in optical densities). For guidelines about units see the Appendix and Appendix pages.

Schema information:

format **:** unit
type **:** string


### uri (formats)

Name: Uniform resource indicator

Type: Format

Regular expression:(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?

Description: A uniform resource indicator.

### value (columns)

Name: Marker value

Type: Column

Description: Marker value associated with the event (for example, the value of a TTL trigger that was recorded at the onset of the event).

Schema information:

anyOf **:**

**-** type **:** number
**-** type **:** string

### vhdr (extensions)

Name: BrainVision Text Header

Type: Extension

Format:<entities>_<suffix>.vhdr

Description: A text header file in theBrainVision Core Data Format. These files come in three-file sets, including a.vhdr, a.vmrk, and a.eegfile.

### vmrk (extensions)

Name: BrainVision Marker

Type: Extension

Format:<entities>_<suffix>.vmrk

Description: A text marker file in theBrainVision Core Data Format. These files come in three-file sets, including a.vhdr, a.vmrk, and a.eegfile.


### volume_type (columns)

Name: ASL volume type

Type: Column

Allowed values:control,label,m0scan,deltam,cbf

Description: The*_aslcontext.tsvtable consists of a single column of labels identifying thevolume_typeof each volume in the corresponding*_asl.nii[.gz]file.

Schema information:

type **:** string

### wavelength_actual (columns)

Name: Wavelength actual

Type: Column

Description: Measuredwavelengthoflightinnm.n/aforchannelsthatdonotcontainrawNIRSsignals(acceleration). ThisfieldisequivalenttomeasurementList.wavelengthActual
in the SNIRF specification.

Schema information:

type **:** number

### wavelength_emission_actual (columns)

Name: Wavelength emission actual

Type: Column

Description: Measured emission wavelength of light in nm. n/afor channels that do not contain raw NIRS signals (acceleration). This field is equivalent to
measurementList.wavelengthEmissionActualin the SNIRF specification.

Schema information:

type **:** number

### wavelength_nominal (columns)

Name: Wavelength nominal

Type: Column


Description: Specified wavelength of light in nm. n/afor channels that do not contain raw NIRS signals (for example, acceleration). This field is equivalent to
/nirs(i)/probe/wavelengthsin the SNIRF specification.

Schema information:

anyOf **:**

**-** type **:** number
**-** enum **:**
    **-** n/a
    type **:** string

### whole_blood_radioactivity (columns)

Name: Whole blood radioactivity

Type: Column

Description: Radioactivity in whole blood samples, in unit of radioactivity measurements in whole blood samples (for example,kBq/mL).

Schema information:

type **:** number

### x sense 1 (columns)

Name: X position

Type: Column

Description: Recorded position along the x-axis.

Schema information:

type **:** number

### x sense 2 (columns)

Name: X position

Type: Column

Description: Recorded position along the x-axis."n/a"if not available.

Schema information:


anyOf **:**

**-** type **:** number
**-** enum **:**
    **-** n/a
    type **:** string

### y sense 1 (columns)

Name: Y position

Type: Column

Description: Recorded position along the y-axis.

Schema information:

type **:** number

### y sense 2 (columns)

Name: Y position

Type: Column

Description: Recorded position along the y-axis."n/a"if not available.

Schema information:

anyOf **:**

**-** type **:** number
**-** enum **:**
    **-** n/a
    type **:** string

### z sense 1 (columns)

Name: Z position

Type: Column

Description: Recorded position along the z-axis.

Schema information:


anyOf **:**

**-** type **:** number
**-** enum **:**
    **-** n/a
    type **:** string

### z sense 2 (columns)

Name: Z position

Type: Column

Description: Recorded position along the z-axis."n/a"if not available.

Schema information:

anyOf **:**

**-** type **:** number
**-** enum **:**
    **-** n/a
    type **:** string


# BIDS Extension Proposals

The BIDS specification can be extended in a backwards compatible way and will evolve over time. This is accomplished with BIDS Extension Proposals (BEPs), which are
community-driven processes (seeBEP guidelines Google Doc).

On theBIDS homepageyou can find alist of extension proposalsthat are currently being worked on.

All changes that are not backwards compatible with the current BIDS specification will be implemented in BIDS2.0. See the correspondingGitHub repository.


# Contributors

Legend (source:https://allcontributors.org/docs/en/emoji-key)

Emoji Represents

💬 Answering Questions (on the mailing list, NeuroStars, GitHub, in person, or
otherwise)
🐛 Bug reports
📝 Blogposts
💻 Code
🖋 Content (separate from Blogposts, for example Website news)
📖 Documentation and specification
🔣 Data (example datasets)
🎨 Design
💡 Examples (for example datasets, useData)
📋 Event Organizers
💵 Financial Support
🔍 Funding/Grant Finders
🤔 Ideas & Planning
🚇 Infrastructure (hosting, build-tools, and so on)
🚧 Maintenance of the BIDS standard
🧑 🏫 Mentoring new contributors
🔌 Plugin/utility libraries
📆 Project management
👀 Reviewed Pull Requests
🔧 Tools
🌍 Translation
⚠ Tests
✅ Tutorials
📢 Talks


Emoji Represents

📓 User testing (of new features, tools, and so on)
📹 Videos

The following individuals have contributed to the Brain Imaging Data Structure ecosystem (in alphabetical order). If you contributed to the BIDS ecosystem and your
name is not listed, please add it.

- Eric Achten 📖🔣📓
- Azeez Adebimpe 📖
- Rémi Adon 📖
- Fidel Alfaro Almagro 💬📖💡🔌
- David Alsop 📖
- Stefan Appelhoff 📖💬🤔🐛💡💻👀⚠📢✅🔧🔌📝🚧🔣
- Yoni Ashar 📖
- Tal Pal Attia 📖
- Tibor Auer 💬📖💡🔧📢🐛🤔
- Sylvain Baillet 📖🔍
- Shashank Bansal 📖
- Arshitha Basavaraj 📖🚇💻
- Ben Beasley 💻
- Leandro Beltrachini 📖
- Chris Benjamin 📖
- Timo Berg 📖
- Étienne Bergeron 🔣💻
- Giacomo Bertazzoli 📖
- Suyash Bhogawar 📖💡⚠🔧💬
- Stephan Bickel 📖
- Ulrike Bingel 📖
- Ethan Blackwood 👀📖
- David Boas 📖
- Elizabeth Bock 📖💡
- Hugo Boniface 📖
- Marta Bortoletto 📖
- Kristofer Bouchard 📖
- Mathieu Boudreau 💬🤔📢
- Marie-Hélène Bourget 📖🔣💻🤔
- Eric Bridgeford 📖🔧
- Teon L. Brooks 📖💻⚠💬👀🤔🔧🐛📢
- Martina Bulgari 📖
- Christian Büchel 📖


- Vince D. Calhoun 📖
- Giulio Castegnaro 📖
- Marco Castellaro 💬🐛💻📖💡⚠📢🚇
- Filippo Maria Castelli 📖🔣
- Michael Chappell 📖🔣📆
- Gang Chen 📖
- William Clarke 📖
- Patricia Clement 💬🐛💻📖🔣💡📋🤔📆⚠📢
- Helena Cockx 📖
- Alexander L. Cohen 🐛💻📖💬
- Julien Cohen-Adad 📖🔣🤔
- R. Cameron Craddock 📖📢
- Martin Craig 🔣
- Sasha D’Ambrosio 📖
- Samir Das 📖
- Olivier David 📖
- Orrin Devinsky 📖
- Gilles de Hollander 📖
- Alejandro de la Vega 🐛💻⚠
- Arnaud Delorme 📖💡
- John Detre 📖
- Benjamin Dichter 📖
- Erin W. Dickie 📖🤔👀📢💬
- Timo Dickscheid 📖
- Dejan Draschkow 📖
- Eugene P. Duff 📖
- Elizabeth DuPre 📖💡🔍🤔💬
- Joke Durnez 📖🔧💻
- Eric Earl 📖💬🐛🚧🔧🤔
- Cyrus Eierud 💻
- Anders Eklund 📖📢💻
- Sara Elgayar 📖
- Oscar Esteban 📖🔧🤔💬💻
- Franklin W. Feingold 📋📝✅💬🤔🎨📢👀🚇🖋📆
- Guillaume Flandin 📖💻
- Adeen Flinker 📖
- Alexandru Foias 📖🔣
- Brett L. Foster 📖
- Ana Fouto 📓
- Benjamin Gagl 📖


- Chris Gahnström 📖
- Anthony Galassi 📖
- Giuseppe Gallitto 📖
- Melanie Ganz-Benjaminsen 📖🔣💻🤔📆🔍📢
- Samuel Garcia 🤔👀📖
- Remi Gau 📖💻💬📢🐛💻🚇👀🔧🤔
- James Gholam 📖
- Satrajit S. Ghosh 📖💻
- Ashley G. Gillman 📖
- Greydon Gilmore 📖
- Tristan Glatard 📖💻
- Mathias Goncalves 💻🔧📢
- Krzysztof J. Gorgolewski 📖💻💬🤔🔍📢📝💡🔌
- Rohan Goyal 💻
- Alexandre Gramfort 📖💡
- Klara Gregorova 📖
- Jeffrey S. Grethe 💬🐛✅📢
- Iris Groen 📖
- David Groppe 📖
- Sören Grothkopp 📖
- Aysegul Gunduz 📖
- Giacomo Guidali 📖
- Matthias Günther 📖
- Yaroslav O. Halchenko 📖📢🔧💬🐛
- Liberty Hamilton 📖
- Tom Hampshire 📖
- Daniel A. Handwerker 📖
- Michael Hanke 📖🤔🔧🐛📢
- Nell Hardcastle 💻 🤔 🚇 💬 👀
- Michael P. Harms 📖⚠🔧
- Soichi Hayashi 📖🔧🐛
- Richard N. Henson 📖
- Peer Herholz 💬📖👀🔧✅📢
- Dora Hermes 📖💻✅🔍🤔
- Luis Hernandez-Garcia 📖📓
- Katja Heuer 🔧
- Dorien Huijser 📖
- Alexandre Hutton 📖
- Richard Höchenberger 📖
- Chris Holdgraf 📖🤔


- Christopher J. Honey 📖
- Andrew Hoopes 📖
- Christian Horea 📖
- Jean-Christophe Houde 📖
- Vittorio Iacovella 📖
- Maria de la Iglesia 📖
- Ilkay Isik 📖
- Hamish Innes-Brown 📖
- International Neuroinformatics Coordinating Facility 💵📋
- Andrew Jahn 📓
- Andrew Janke 📖💻
- Mainak Jas 📖💻
- Sein Jeung 📖
- Alexander Jones 💻🐛
- Tamás Józsa 📓
- Jakub Kaczmarzyk 📖🔧🚇
- Lee Kamentsky 📖
- Agah Karakuzu 💬📖🔣🤔
- David Keator 📖
- James Kent 💬💻
- Ali Khan 📖
- Gregory Kiar 📖💻🎨🔧
- Balint Kincses 📖
- Thomas Kirk 📖
- Robert Knight 📖
- Joost Kuijer 📖
- Jean-Philippe Lachaux 📖
- Marc Lalancette 📖
- Pamela LaMontagne 📖💡
- Kevin Larcher 💬
- Jonathan C. Lau 📖
- Laura and John Arnold Foundation 💵
- Alexander von Lautz 📖
- Alberto Lazari 📖
- Kangjoo Lee 📖
- Christopher Lee-Messer 📖
- Jon Haitz Legarreta 💻📖
- Dan Levitas 📖
- Adam Li 📖💻
- Xiangrui Li 📖💻


- Ilona Lipp 📖
- Vladimir Litvak 📖
- Hanzhang Lu 📖
- Robert Luke 📖
- Brian N. Lundstrom 📖
- Dan Lurie 🤔📖🔧🔌💻💬
- Duncan Macleod 🚇
- Eleonora Marcantoni 📖
- Christopher J. Markiewicz 💬🐛💻📖🎨💡🤔🔌👀🔧📢🔣📋🚧
- Camille Maumet 📖
- Giacomo Mazzamuto 📖🔣
- David McAlpine 📖
- Manuel Mercier 📖🤔
- Mark Mikkelsen 📖
- Kai J. Miller 📖
- Carlo Miniussi 📖
- Markus Morawski 📖
- Clara Moreau 📖
- Jeremy Moreau 📖💡
- Zachary Michael 📖
- Ezequiel Mikulan 📖💻
- Michael P. Milham 💡🔍
- Jeanette Mumford 📖
- Athanasia Monika Mowinckel 📖
- Henk Mutsaerts 💬🐛💻📖💡📋🤔📆📢📓
- Manjari Narayan 📖
- National Institute of Mental Health 💵
- Mikael Naveau 🐛
- B. Nolan Nichols 📖
- Thomas E. Nichols 📖📢🔧👀🚧
- Dylan Nielson 📖💻🔧
- Aki Nikolaidis 📖
- Gustav Nilsonne 📖
- Guiomar Niso 🤔🎨🔍👀📋📝🔧🐛💻🔣✅💬📖💡📢
- Gregory Noack 💻 ⚠
- Martin Noergaard 📖🔣💻🤔📢
- Michael P. Notter 💬📝✅📢📖
- Jeffrey G. Ojemann 📖
- Thomas Okell 📖
- Aaron Oliver-Taylor 📖


- Hernando Ombao 📖
- Robert Oostenveld 📖🔧📢💡✅⚠🤔💬🐛📝💻🖋🔣🎨📋🚇👀📓📹
- Dimitri Papadopoulos Orfanos 📖💡🤔💬
- Felipe Orihuela-Espina 📖
- Eduard Ort 📖
- Patrick Park 📖💡💬
- Maurice Pasternak 📓
- Chloé Pasturel 📖
- Dianne Patterson 📖
- Mateusz Pawlik 🤔 📖 🚧 👀 🐛
- John Pellman 📖
- Cyril Pernet 💬📝📖🎨💡📋🤔📢
- Franco Pestilli 📖💻🎨💡🤔👀🔧📋🔍🚇
- Jan Petr 💬🐛💻📖🔣💡📋🤔📆⚠📢
- Natalia Petridou 📖
- Dmitry Petrov 📖💻
- Christophe Phillips 📖
- Gio Piantoni 📖
- Andrea Pigorini 📖
- Russell A. Poldrack 📖🔍📢
- Jean-Baptiste Poline 📖📢🤔🎨
- Luca Pollonini 📖
- Wouter V. Potters 📖
- Nader Pouratian 📖
- Pradeep Reddy Raamana 💻🔧
- Vasudev Raguram 💻🎨📖🔧
- Nick F. Ramsey 📖
- Travis Riddle 📖🔧🐛
- Pierre Rioux 📖
- Petra Ritter 📖
- Kay Robbins 💻📖🐛
- Alex Rockhill 📖🔧
- Ariel Rokem 📖
- Chris Rorden 📖💻
- Jose Manuel Saborit 📖
- Taylor Salo 💬📖🔌
- Matt Sanderson 📖💻
- Gunnar Schaefer 📖
- Michael Schirner 📖
- Jan-Mathijs Schoffelen 📖


- Graham Searle 📖
- Parul Sethi 📖🔧⚠💻
- Maureen J Shader 📖
- Robert E. Smith 💻📖
- Vanessa Sochat 📖
- Anibal Sólon 🐛
- Tamas Spisak 📖
- Julia Sprenger 📖
- Isla Staden 📖
- Arjen Stolk 📖
- Nicole C. Swann 📖
- Filip Szczepankiewicz 📖
- Martin Szinte 📖
- François Tadel 📖🔌💡
- Sylvain Takerkart 📖
- Bertrand Thirion 📖
- David Thomas 📖🔣
- Roberto Toro 🔧
- Sébastien Tourbier 🤔👀📢🐛💻📖
- Paule-Joanne Toussaint 📖
- Nicholas Traut 📖🔧💻
- William Triplett 📖
- Jessica A. Turner 📖
- Pieter Vandemaele 📖💻
- Max A. van den Boom 💻👀📖🐛
- Wietske van der Zwaag 🔣💬
- Matthias Van Osch 📖
- Gaël Varoquaux 📖
- Jaap von der Aar 📖
- Sjoerd Vos 📖
- Bradley Voytek 📖
- Tor Wager 📖
- Adina S. Wagner 🎨
- Lennart Walger 📖
- Brian A. Wandell 📖
- Hao Ting Wang 📖🐛
- Yuan Wang 💻
- Julius Welzel 📖
- Joseph Wexler 📖💡
- Kirstie Whitaker 📖💡🔍🤔📢💬


- Martin Wilson 📖
- Jonathan Winawer 📖
- Lennart Wittkuhn 📖
- Joseph Woods 📖
- Tal Yarkoni 💻📖🤔🔍🔌👀📢🐛🎨
- Lyuba Zehl 📖


# Licenses

This section lists a number of common licenses for datasets and defines suggested abbreviations for use in the dataset metadata specifications.

Pleasenotethatthislistonlyservestoprovidesomeexamplesforpossiblelicenses. Thetermsofanylicenseshouldbeconsistentwiththeinformedconsentobtainedfrom
participants and any institutional limitations on distribution.

```
Identifier License name Description
PD Public Domain No license required for any purpose; the work is not
subject to copyright in any jurisdiction.
PDDL Open Data Commons Public Domain Dedication and
License
```
```
License to assign public domain like permissions
without giving up the copyright.
CC0 Creative Commons Zero 1.0 Universal. Use this if you are a holder of copyright or database
rights, and you wish to waive all your interests in
your work worldwide.
```

# Entity table

This section compiles the entities (key-value pairs within file names) described throughout this specification, and establishes a common order within a filename. For
example, if a file has an acquisition and reconstruction label, the acquisition entity must precede the reconstruction entity. REQUIRED and OPTIONAL entities for a
given file type are denoted; empty cells imply that entities MUST NOT be specified. Entity formats indicate whether the value is alphanumeric (<label>) or numeric
(<index>).

A general introduction to entities is given in the section on filename structure, while entity definitions are in the Entities Appendix.

## Magnetic Resonance Imaging

```
Entity Subject Session Task AcquisitionContrast
En-
hanc-
ing
Agent
```
```
ReconstructionPhase-
Encoding
Direc-
tion
```
```
Run Corresponding
Modal-
ity
```
```
Echo Flip
Angle
```
```
Inversion
Time
```
```
Magnetization
Trans-
fer
```
```
Part Recording
```
```
Format sub-<label>sub-<label>sub-<label>sub-<label>sub-<label>sub-<label>sub-<label>sub-<label>sub-<label>sub-<label>sub-<label>sub-<label>sub-<label>sub-<label>sub-<label>
anat(IRT1)REQUIREDOPTIONAL OPTIONALOPTIONALOPTIONAL OPTIONAL REQUIRED OPTIONAL
anat(MESE
anat)
```
##### REQUIREDOPTIONAL OPTIONALOPTIONALOPTIONAL OPTIONAL REQUIRED OPTIONAL

```
anat(MP2RAGE)REQUIREDOPTIONAL OPTIONALOPTIONALOPTIONAL OPTIONAL OPTIONALOPTIONALREQUIRED OPTIONAL
anat(MPM
anat)
```
##### REQUIREDOPTIONAL OPTIONALOPTIONALOPTIONAL OPTIONAL OPTIONALREQUIRED REQUIREDOPTIONAL

```
anat(MTR)REQUIREDOPTIONAL OPTIONALOPTIONALOPTIONAL OPTIONAL REQUIREDOPTIONAL
```

Entity Subject Session Task AcquisitionContrast
En-
hanc-
ing
Agent

```
ReconstructionPhase-
Encoding
Direc-
tion
```
```
Run Corresponding
Modal-
ity
```
```
Echo Flip
Angle
```
```
Inversion
Time
```
```
Magnetization
Trans-
fer
```
```
Part Recording
```
anat(T1map
anat
anat
anat
anat
anat
anat
anat
anat
anat
anat
anat
anat
anat
anat
anat
anat)

##### REQUIREDOPTIONAL OPTIONALOPTIONALOPTIONAL OPTIONAL

anat(T1w
anat
anat
anat
anat
anat
anat
anat
anat
anat
anat
anat)

##### REQUIREDOPTIONAL OPTIONALOPTIONALOPTIONAL OPTIONAL OPTIONAL

anat(VFA)REQUIREDOPTIONAL OPTIONALOPTIONALOPTIONAL OPTIONAL OPTIONALREQUIRED OPTIONAL
anat(defacemaskREQUIREDOPTIONAL) OPTIONALOPTIONALOPTIONAL OPTIONALOPTIONAL
dwi(dwi
dwi)

##### REQUIREDOPTIONAL OPTIONAL OPTIONALOPTIONALOPTIONAL OPTIONAL

dwi(physio
dwi)

##### REQUIREDOPTIONALREQUIREDOPTIONAL OPTIONALOPTIONALOPTIONAL OPTIONAL


```
Entity Subject Session Task AcquisitionContrast
En-
hanc-
ing
Agent
```
```
ReconstructionPhase-
Encoding
Direc-
tion
```
```
Run Corresponding
Modal-
ity
```
```
Echo Flip
Angle
```
```
Inversion
Time
```
```
Magnetization
Trans-
fer
```
```
Part Recording
```
```
fmap(TB1AFI
fmap
fmap
fmap)
```
##### REQUIREDOPTIONAL OPTIONALOPTIONALOPTIONAL OPTIONAL OPTIONALOPTIONALOPTIONAL OPTIONAL

```
fmap(TB1DAM)REQUIREDOPTIONAL OPTIONALOPTIONALOPTIONAL OPTIONAL REQUIREDOPTIONAL OPTIONAL
fmap(TB1EPIREQUIRED) OPTIONAL OPTIONALOPTIONALOPTIONAL OPTIONAL REQUIREDREQUIREDOPTIONAL OPTIONAL
fmap(TB1SRGE)REQUIREDOPTIONAL OPTIONALOPTIONALOPTIONAL OPTIONAL OPTIONALREQUIREDREQUIRED OPTIONAL
fmap(TB1map
fmap)
```
##### REQUIREDOPTIONAL OPTIONALOPTIONALOPTIONAL OPTIONAL

```
fmap(epi
fmap)
```
##### REQUIREDOPTIONAL OPTIONALOPTIONAL REQUIREDOPTIONAL

```
fmap(phasediff
fmap
fmap
fmap
fmap
fmap
fmap)
```
##### REQUIREDOPTIONAL OPTIONAL OPTIONAL

```
func(bold
func
func)
```
##### REQUIREDOPTIONALREQUIREDOPTIONALOPTIONALOPTIONALOPTIONALOPTIONAL OPTIONAL OPTIONAL

```
func(eventsREQUIRED) OPTIONALREQUIREDOPTIONALOPTIONALOPTIONALOPTIONALOPTIONAL
func(phase)REQUIREDOPTIONALREQUIREDOPTIONALOPTIONALOPTIONALOPTIONALOPTIONAL OPTIONAL
func(physio
func)
```
##### REQUIREDOPTIONALREQUIREDOPTIONALOPTIONALOPTIONALOPTIONALOPTIONAL OPTIONAL

```
perf(asl
perf
perf)
```
##### REQUIREDOPTIONAL OPTIONAL OPTIONALOPTIONALOPTIONAL

```
perf(asllabelingREQUIRED) OPTIONAL OPTIONAL OPTIONAL OPTIONAL
perf(physio
perf)
```
##### REQUIREDOPTIONALREQUIREDOPTIONAL OPTIONALOPTIONALOPTIONAL OPTIONAL

### Biopotential Amplification (EEG and iEEG)


```
Entity Subject Session Task Acquisition Run Space Recording
Format sub-<label> sub-<label> sub-<label> sub-<label> sub-<label> sub-<label> sub-<label>
eeg(channelseeg
eeg)
```
##### REQUIRED OPTIONAL REQUIRED OPTIONAL OPTIONAL

```
eeg(coordsystem
eeg)
```
##### REQUIRED OPTIONAL OPTIONAL OPTIONAL

```
eeg(photo) REQUIRED OPTIONAL OPTIONAL
eeg(physioeeg) REQUIRED OPTIONAL REQUIRED OPTIONAL OPTIONAL OPTIONAL
ieeg(channelsieeg
ieeg)
```
##### REQUIRED OPTIONAL REQUIRED OPTIONAL OPTIONAL

```
ieeg(coordsystem
ieeg)
```
##### REQUIRED OPTIONAL OPTIONAL OPTIONAL

```
ieeg(photo) REQUIRED OPTIONAL OPTIONAL
ieeg(physioieeg) REQUIRED OPTIONAL REQUIRED OPTIONAL OPTIONAL OPTIONAL
```
### Magnetoencephalography (MEG)

Entity Subject Session Task Acquisition Run Processed (on
device)

```
Space Split Recording
```
Format sub-<label> sub-<label> sub-<label> sub-<label> sub-<label> sub-<label> sub-<label> sub-<label> sub-<label>
meg(channels) REQUIRED OPTIONAL REQUIRED OPTIONAL OPTIONAL OPTIONAL
meg(coordsystem
meg meg)

##### REQUIRED OPTIONAL OPTIONAL

meg(events) REQUIRED OPTIONAL REQUIRED OPTIONAL OPTIONAL
meg(markers) REQUIRED OPTIONAL OPTIONAL OPTIONAL OPTIONAL
meg(meg
meg)

##### REQUIRED OPTIONAL REQUIRED

meg(meg) REQUIRED OPTIONAL REQUIRED OPTIONAL OPTIONAL OPTIONAL OPTIONAL
meg(physio
meg)

##### REQUIRED OPTIONAL REQUIRED OPTIONAL OPTIONAL OPTIONAL

### Positron Emission Tomography (PET)


```
Entity Subject Session Task Tracer Reconstruction Run Recording
Format sub-<label> sub-<label> sub-<label> sub-<label> sub-<label> sub-<label> sub-<label>
pet(blood) REQUIRED OPTIONAL OPTIONAL OPTIONAL OPTIONAL OPTIONAL REQUIRED
pet(events) REQUIRED OPTIONAL REQUIRED OPTIONAL OPTIONAL OPTIONAL
pet(pet) REQUIRED OPTIONAL OPTIONAL OPTIONAL OPTIONAL OPTIONAL
pet(physiopet) REQUIRED OPTIONAL REQUIRED OPTIONAL OPTIONAL OPTIONAL OPTIONAL
```
### Behavioral Data

```
Entity Subject Session Task Acquisition Run Recording
Format sub-<label> sub-<label> sub-<label> sub-<label> sub-<label> sub-<label>
beh(behbeh) REQUIRED OPTIONAL REQUIRED OPTIONAL OPTIONAL
beh(physiobeh) REQUIRED OPTIONAL REQUIRED OPTIONAL OPTIONAL OPTIONAL
```
### Microscopy

```
Entity Subject Session Sample Acquisition Stain Run Chunk
Format sub-<label> sub-<label> sub-<label> sub-<label> sub-<label> sub-<label> sub-<label>
micr(TEMmicr
micr micr micr
micr micr micr
micr micr micr
micr micr micr
micr micr micr)
```
##### REQUIRED OPTIONAL REQUIRED OPTIONAL OPTIONAL OPTIONAL OPTIONAL

```
micr(photo) REQUIRED OPTIONAL REQUIRED OPTIONAL
```

# Entities

This section compiles the entities (key-value pairs within file names) described throughout this specification, and describes each.

A general introduction to entities is given in the section on filename structure.

The ordering of entities, and whether each is OPTIONAL, REQUIRED, or MUST NOT be specified for a given file type, is specified in the Entity Table.

## sub

Full name: Subject

Format:sub-<label>

Definition: A person or animal participating in the study.

## ses

Full name: Session

Format:ses-<label>

Definition: Alogicalgroupingofneuroimagingandbehavioraldataconsistentacrosssubjects. Sessioncan(butdoesn’thaveto)besynonymoustoavisitinalongitudinal
study. In general, subjects will stay in the scanner during one session. However, for example, if a subject has to leave the scanner room and then be re-positioned on the
scanner bed, the set of MRI acquisitions will still be considered as a session and match sessions acquired in other subjects. Similarly, in situations where different data
types are obtained over several visits (for example fMRI on one day followed by DWI the day after) those can be grouped in one session.

Defining multiple sessions is appropriate when several identical or similar data acquisitions are planned and performed on all -or most- subjects, often in the case of some
intervention between sessions (for example, training).


### sample

```
Full name: Sample
Format:sample-<label>
Definition: A sample pertaining to a subject such as tissue, primary cell or cell-free sample. Thesample-<label>entity is used to distinguish between different samples
from the same subject. The label MUST be unique per subject and is RECOMMENDED to be unique throughout the dataset.
```
### task

```
Full name: Task
Format:task-<label>
Definition: A set of structured activities performed by the participant. Tasks are usually accompanied by stimuli and responses, and can greatly vary in complexity.
In the context of brain scanning, a task is always tied to one data acquisition. Therefore, even if during one acquisition the subject performed multiple conceptually
different behaviors (with different sets of instructions) they will be considered one (combined) task.
```
Whiletasksmayberepeatedacrossmultipleacquisitions,agiventaskmayhavedifferentsetsofstimuli(forexample,randomizedorder)andparticipantresponsesacross
subjects, sessions, and runs.
Thetask-<label>MUST be consistent across subjects and sessions.
Files with thetask-<label>entity SHOULD have an associated events file, as well as certain metadata fields in the associated JSON file.
For the purpose of this specification we consider the so-called ”resting state” a task, although events files are not expected for resting state data. Additionally, a common
convention in the specification is to include the word ”rest” in thetasklabel for resting state files (for example,task-rest).

### acq

```
Full name: Acquisition
Format:acq-<label>
Definition: Theacq-<label>entity corresponds to a custom label the user MAY use to distinguish a different set of parameters used for acquiring the same modality.
For example, this should be used when a study includes two T1w images - one full brain low resolution and one restricted field of view but high resolution. In such case
two files could have the following names:sub-01_acq-highres_T1w.nii.gzandsub-01_acq-lowres_T1w.nii.gz; however, the user is free to choose any other label
thanhighresandlowresas long as they are consistent across subjects and sessions.
In case different sequences are used to record the same modality (for example,RAREandFLASHfor T1w) this field can also be used to make that distinction. The level
of detail at which the distinction is made (for example, just betweenRAREandFLASH, or betweenRARE,FLASH, andFLASHsubsampled) remains at the discretion of the
researcher.
```

### ce

Full name: Contrast Enhancing Agent

Format:ce-<label>

Definition: Thece-<label>entity can be used to distinguish sequences using different contrast enhanced images. The label is the name of the contrast agent.

This entity represents the"ContrastBolusIngredient"metadata field. Therefore, if thece-<label>entity is present in a filename,"ContrastBolusIngredient"MAY
also be added in the JSON file, with the same label.

### trc

Full name: Tracer

Format:trc-<label>

Definition: Thetrc-<label>entity can be used to distinguish sequences using different tracers.

This entity represents the"TracerName"metadata field. Therefore, if thetrc-<label>entity is present in a filename,"TracerName"MUST be defined in the associated
metadata. Please note that the<label>does not need to match the actual value of the field.

### stain

Full name: Stain

Format:stain-<label>

Definition: Thestain-<label>key/pair values can be used to distinguish image files from the same sample using different stains or antibodies for contrast enhancement.

This entity represents the"SampleStaining"metadata field. Therefore, if thestain-<label>entity is present in a filename,"SampleStaining"SHOULD be defined in
the associated metadata, although the label may be different.

Descriptions of antibodies SHOULD also be indicated in the"SamplePrimaryAntibodies"and/or"SampleSecondaryAntobodies"metadata fields, as appropriate.

### rec

Full name: Reconstruction

Format:rec-<label>

Definition: Therec-<label>entity can be used to distinguish different reconstruction algorithms (for example,MoCofor the ones using motion correction).


### dir

Full name: Phase-Encoding Direction

Format:dir-<label>

Definition: Thedir-<label>entity can be set to an arbitrary alphanumeric label (for example,dir-LRordir-AP) to distinguish different phase-encoding directions.

This entity represents the"PhaseEncodingDirection"metadata field. Therefore, if thedir-<label>entity is present in a filename,"PhaseEncodingDirection"MUST
be defined in the associated metadata. Please note that the<label>does not need to match the actual value of the field.

### run

Full name: Run

Format:run-<index>

Definition: Therun-<index>entity is used to distinguish separate data acquisitions with the same acquisition parameters and (other) entities.

If several data acquisitions (for example, MRI scans or EEG recordings) with the same acquisition parameters are acquired in the same session, they MUST be indexed
with therun-<index>entity:_run-1,_run-2,_run-3, and so on (only nonnegative integers are allowed as run indices).

If different entities apply, such as a different session indicated by [ses-<label>][../../appendices/entities.md#ses), or different acquisition parameters indicated by
acq-<label>, thenrunis not needed to distinguish the scans and MAY be omitted.

### mod

Full name: Corresponding Modality

Format:mod-<label>

Definition: Themod-<label>entity corresponds to modality label for defacing masks, for example, T1w, inplaneT1, referenced by a defacemask image. For example,
sub-01_mod-T1w_defacemask.nii.gz.

### echo

Full name: Echo

Format:echo-<index>

Definition: If files belonging to an entity-linked file collection are acquired at different echo times, theecho-<index>entity MUST be used to distinguish individual files.

This entity represents the"EchoTime"metadata field. Therefore, if theecho-<index>entity is present in a filename,"EchoTime"MUST be defined in the associated
metadata. Please note that the<index>denotes the number/index (in the form of a nonnegative integer), not the"EchoTime"value of the separate JSON file.


### flip

Full name: Flip Angle

Format:flip-<index>

Definition: If files belonging to an entity-linked file collection are acquired at different flip angles, the_flip-<index>entity pair MUST be used to distinguish individual
files.

This entity represents the"FlipAngle"metadata field. Therefore, if theflip-<index>entity is present in a filename,"FlipAngle"MUST be defined in the associated
metadata. Please note that the<index>denotes the number/index (in the form of a nonnegative integer), not the"FlipAngle"value of the separate JSON file.

### inv

Full name: Inversion Time

Format:inv-<index>

Definition: If files belonging to an entity-linked file collection are acquired at different inversion times, theinv-<index>entity MUST be used to distinguish individual
files.

This entity represents the"InversionTimemetadata field. Therefore, if theinv-<index>entity is present in a filename,"InversionTime"MUST be defined in the
associatedmetadata. Pleasenotethatthe<index>denotesthenumber/index(intheformofanonnegativeinteger),notthe"InversionTime"valueoftheseparateJSON
file.

### mt

Full name: Magnetization Transfer

Format:mt-<label>

Allowed values:on,off

Definition: If files belonging to an entity-linked file collection are acquired at different magnetization transfer (MT) states, the_mt-<label>entity MUST be used to
distinguish individual files.

Thisentityrepresentsthe"MTState"metadatafield. Therefore, ifthemt-<label>entityispresentinafilename,"MTState"MUSTbedefinedintheassociatedmetadata.
Allowed label values for this entity areonandoff, for images acquired in presence and absence of an MT pulse, respectively.

### part

Full name: Part

Format:part-<label>


```
Allowed values:mag,phase,real,imag
Definition: This entity is used to indicate which component of the complex representation of the MRI signal is represented in voxel data. Thepart-<label>entity is
associated with the DICOM Tag0008, 9208. Allowed label values for this entity arephase,mag,realandimag, which are typically used inpart-mag/part-phaseor
part-real/part-imagpairs of files.
Phase images MAY be in radians or in arbitrary units. The sidecar JSON file MUST include the units of thephaseimage. The possible options are"rad"or"arbitrary".
```
When there is only a magnitude image of a given type, thepartentity MAY be omitted.

### proc

```
Full name: Processed (on device)
Format:proc-<label>
Definition: The proc label is analogous to rec for MR and denotes a variant of a file that was a result of particular processing performed on the device.
This is useful for files produced in particular by Elekta’s MaxFilter (for example,sss,tsss,trans,quatormc), which some installations impose to be run on raw data
because of active shielding software corrections before the MEG data can actually be exploited.
```
### hemi

```
Full name: Hemisphere
Format:hemi-<label>
Allowed values:L,R
Definition: Thehemi-<label>entity indicates which hemibrain is described by the file. Allowed label values for this entity areLandR, for the left and right hemibrains,
respectively.
```
### space

```
Full name: Space
Format:space-<label>
Definition: Thespace-<label>entity can be used to indicate the way in which electrode positions are interpreted (for EEG/MEG/iEEG data) or the spatial reference to
which a file has been aligned (for MRI data). The<label>MUST be taken from one of the modality specific lists in the Coordinate Systems Appendix. For example, for
iEEG data, the restricted keywords listed under iEEG Specific Coordinate Systems are acceptable for<label>.
For EEG/MEG/iEEG data, this entity can be applied to raw data, but for other data types, it is restricted to derivative data.
```

### split

Full name: Split

Format:split-<index>

Definition: Inthecaseoflongdatarecordingsthatexceedafilesizeof2Gb,.fiffilesareconventionallysplitintomultipleparts. Eachofthesefileshasaninternalpointer
to the next file. This is important when renaming these split recordings to the BIDS convention.

Instead of a simple renaming, files should be read in and saved under their new names with dedicated tools likeMNE-Python, which will ensure that not only the file
names, but also the internal file pointers, will be updated.

It is RECOMMENDED that.fiffiles with multiple parts use thesplit-<index>entity to indicate each part. If there are multiple parts of a recording and the optional
scans.tsvisprovided,allfilesMUSTbelistedseparatelyinscans.tsvandtheentriesfortheacq_timecolumninscans.tsvMUSTallbeidentical,asdescribedinScans
file.

### recording

Full name: Recording

Format:recording-<label>

Definition: Therecording-<label>entity can be used to distinguish continuous recording files.

This entity is commonly applied when continuous recordings have different sampling frequencies or start times. For example, physiological recordings with different
sampling frequencies may be distinguished using labels likerecording-100Hzandrecording-500Hz.

### chunk

Full name: Chunk

Format:chunk-<index>

Definition: Thechunk-<index>key/value pair is used to distinguish between different regions, 2D images or 3D volumes files, of the same physical sample with different
fields of view acquired in the same imaging experiment.

### atlas

Full name: Atlas

Format:atlas-<label>

Definition: Theatlas-<label>key/value pair corresponds to a custom label the user MAY use to distinguish a different atlas used for similar type of data.

This entity is only applicable to derivative data.


### res

Full name: Resolution

Format:res-<label>

Definition: Resolution of regularly sampled N-dimensional data.

Thisentityrepresentsthe"Resolution"metadatafield. Therefore,iftheres-<label>entityispresentinafilename,"Resolution"MUSTalsobeaddedintheJSONfile,
to provide interpretation.

This entity is only applicable to derivative data.

### den

Full name: Density

Format:den-<label>

Definition: Density of non-parametric surfaces.

This entity represents the"Density"metadata field. Therefore, if theden-<label>entity is present in a filename,"Density"MUST also be added in the JSON file, to
provide interpretation.

This entity is only applicable to derivative data.

### label

Full name: Label

Format:label-<label>

Definition: Tissue-typelabel,followingaprescribedvocabulary. Appliestobinarymasksandprobabilistic/partialvolumesegmentationsthatdescribeasingletissuetype.

This entity is only applicable to derivative data.

### desc

Full name: Description

Format:desc-<label>

Definition: When necessary to distinguish two files that do not otherwise have a distinguishing entity, thedesc-<label>entity SHOULD be used.

This entity is only applicable to derivative data.


# File collections

Here, some concrete use-cases of entity-linked file collections are listed using descriptive tables, organized by modality.

The tables in this appendix catalog applications where the use of a file collection is REQUIRED.

Certain entities interlink the files in a file collection through a metadata field. Unlike other common entities (for examplerun), they require an iteration over different
values of the metadata fields they represent. Please keep the following list of linking entities up-to-date with the file collections included in this appendix:

- Magnetic Resonance Imaging
    - echo
    - flip
    - inv
    - mt
    - part

## Magnetic Resonance Imaging

#### Anatomy imaging data

Template:

sub-<label>/
[ses-<label>/]
anat/
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>]_echo-<index>[_part-<mag|phase|real|imag>]_MEGRE.json
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>]_echo-<index>[_part-<mag|phase|real|imag>]_MEGRE.nii[.gz]
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>]_echo-<index>[_part-<mag|phase|real|imag>]_MESE.json
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>]_echo-<index>[_part-<mag|phase|real|imag>]_MESE.nii[.gz]
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>][_echo-<index>]_flip-<index>[_part-<mag|phase|real|imag>]_VFA.json
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>][_echo-<index>]_flip-<index>[_part-<mag|phase|real|imag>]_VFA.nii[.gz]
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>]_inv-<index>[_part-<mag|phase|real|imag>]_IRT1.json


```
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>]_inv-<index>[_part-<mag|phase|real|imag>]_IRT1.nii[.gz]
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>][_echo-<index>][_flip-<index>]_inv-<index>[_part-<mag|phase|real|imag>]_MP2RAGE.json
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>][_echo-<index>][_flip-<index>]_inv-<index>[_part-<mag|phase|real|imag>]_MP2RAGE.nii[.gz]
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>][_echo-<index>]_flip-<index>_mt-<on|off>[_part-<mag|phase|real|imag>]_MPM.json
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>][_echo-<index>]_flip-<index>_mt-<on|off>[_part-<mag|phase|real|imag>]_MPM.nii[.gz]
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>][_echo-<index>]_flip-<index>_mt-<on|off>[_part-<mag|phase|real|imag>]_MTS.json
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>][_echo-<index>]_flip-<index>_mt-<on|off>[_part-<mag|phase|real|imag>]_MTS.nii[.gz]
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>]_mt-<on|off>[_part-<mag|phase|real|imag>]_MTR.json
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>]_mt-<on|off>[_part-<mag|phase|real|imag>]_MTR.nii[.gz]
```
Legend:

- Filename entities or directories between square brackets (for example,[_ses-<label>]) are OPTIONAL.
- Some entities may only allow specific values, in which case those values are listed in<>, separated by|.
- _<suffix>means that there are several (>6) valid suffixes for this filename pattern.
- .<extension>means that there are several (>6) valid extensions for this file type.
- [.gz]means that both the unzipped and gzipped versions of the extension are valid.

Suffix Linking entities Application Description

VFA flip Variable flip angle The VFA method involves at least two
spoiled gradient echo (SPGR) of
steady-state free precession (SSFP)
images acquired at different flip angles.
Depending on the provided metadata
fields and the sequence type, data may
be eligible for DESPOT1, DESPOT2 and
their variants (Deoni et al. 2005).
IRT1 inv, part Inversion recovery T1 mapping The IRT1 method involves multiple
inversion recovery spin-echo images
acquired at different inversion times
(Barral et al. 2010).
MP2RAGE flip, inv, echo, part Magnetization prepared two gradient
echoes

```
The MP2RAGE method is a special
protocol that collects several images at
different flip angles and inversion times
to create a parametric T1map by
combining the magnitude and phase
images (Marques et al. 2010).
```

Suffix Linking entities Application Description

MESE echo Multi-echo spin-echo The MESE method involves multiple
spin echo images acquired at different
echo times and is primarily used for T2
mapping. Please note that this suffix is
not intended for the logical grouping of
images acquired using an Echo Planar
Imaging (EPI) readout.
MEGRE echo Multi-echo gradient-echo Anatomical gradient echo images
acquired at different echo times. Please
note that this suffix is not intended for
the logical grouping of images acquired
using an Echo Planar Imaging (EPI)
readout.
MTR mt Magnetization transfer ratio This method is to calculate a
semi-quantitative magnetization
transfer ratio map.
MTS flip, mt Magnetization transfer saturation This method is to calculate a
semi-quantitative magnetization
transfer saturation index map. The
MTS method involves three sets of
anatomical images that differ in terms
of application of a magnetization
transfer RF pulse (MTon or MToff) and
flip angle (Helms et al. 2008).
MPM flip, mt, echo, part Multi-parametric mapping The MPM approaches (a.k.a hMRI)
involves the acquisition of
highly-similar anatomical images that
differ in terms of application of a
magnetization transfer RF pulse (MTon
or MToff), flip angle and (optionally)
echo time and magnitue/phase parts
(Weiskopf et al. 2013). Seeherefor
suggested MPM acquisition protocols.

#### Fieldmap data

Template:

sub-<label>/


```
[ses-<label>/]
fmap/
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>]_flip-<index>[_inv-<index>][_part-<mag|phase|real|imag>]_TB1DAM.json
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>]_flip-<index>[_inv-<index>][_part-<mag|phase|real|imag>]_TB1DAM.nii[.gz]
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>]_echo-<index>_flip-<index>[_inv-<index>][_part-<mag|phase|real|imag>]_TB1EPI.json
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>]_echo-<index>_flip-<index>[_inv-<index>][_part-<mag|phase|real|imag>]_TB1EPI.nii[.gz]
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>][_echo-<index>][_flip-<index>][_inv-<index>][_part-<mag|phase|real|imag>]_RB1COR.json
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>][_echo-<index>][_flip-<index>][_inv-<index>][_part-<mag|phase|real|imag>]_RB1COR.nii[.gz]
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>][_echo-<index>][_flip-<index>][_inv-<index>][_part-<mag|phase|real|imag>]_TB1AFI.json
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>][_echo-<index>][_flip-<index>][_inv-<index>][_part-<mag|phase|real|imag>]_TB1AFI.nii[.gz]
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>][_echo-<index>][_flip-<index>][_inv-<index>][_part-<mag|phase|real|imag>]_TB1RFM.json
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>][_echo-<index>][_flip-<index>][_inv-<index>][_part-<mag|phase|real|imag>]_TB1RFM.nii[.gz]
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>][_echo-<index>][_flip-<index>][_inv-<index>][_part-<mag|phase|real|imag>]_TB1TFL.json
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>][_echo-<index>][_flip-<index>][_inv-<index>][_part-<mag|phase|real|imag>]_TB1TFL.nii[.gz]
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>][_echo-<index>]_flip-<index>_inv-<index>[_part-<mag|phase|real|imag>]_TB1SRGE.json
sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>][_echo-<index>]_flip-<index>_inv-<index>[_part-<mag|phase|real|imag>]_TB1SRGE.nii[.gz]
```
Legend:

- Filename entities or directories between square brackets (for example,[_ses-<label>]) are OPTIONAL.
- Some entities may only allow specific values, in which case those values are listed in<>, separated by|.
- _<suffix>means that there are several (>6) valid suffixes for this filename pattern.
- .<extension>means that there are several (>6) valid extensions for this file type.
- [.gz]means that both the unzipped and gzipped versions of the extension are valid.

Suffix Meta-data relevant entity Application Description

TB1DAM flip Double-angle B1+ mapping The double-angle B1+ method (Insko
and Bolinger 1993) is based on the
calculation of the actual angles from
signal ratios, collected by two
acquisitions at different nominal
excitation flip angles. Common
sequence types for this application
include spin echo and echo planar
imaging.


Suffix Meta-data relevant entity Application Description

TB1EPI flip, echo B1+ mapping with 3D EPI This B1+ mapping method (Jiru and
Klose 2006) is based on two EPI
readouts to acquire spin echo (SE) and
stimulated echo (STE) images at
multiple flip angles in one sequence,
used in the calculation of deviations
from the nominal flip angle.
TB1AFI Please see the qMRI appendix. Actual Flip Angle Imaging (AFI) This method (Yarnykh 2007) calculates
a B1+ map from two images acquired
at interleaved (two) TRs with identical
RF pulses using a steady-state
sequence.
TB1TFL Please see the qMRI appendix. Siemenstfl_b1_map B1+ data acquired usingtfl_b1_map
product sequence by Siemens based on
the method byChung et al. (2010). The
sequence generates one anatomical
image and one scaled flip angle map.
TB1RFM Please see the qMRI appendix. Siemensrf_map B1+ data acquired usingrf_map
product sequence by Siemens.
TB1SRGE flip,inv SA2RAGE Saturation-prepared with 2 rapid
gradient echoes (SA2RAGE) uses a ratio
of two saturation recovery images with
different time delays, and a simulated
look-up table to estimate B1+
(Eggenschwiler et al. 2011). This
sequence can also be used in
conjunction with MP2RAGE T1
mapping to iteratively improve B1+
and T1 map estimation (Marques &
Gruetter 2013).
RB1COR Please see the qMRI appendix. B1- field correction Low resolution images acquired by the
body coil (in the gantry of the scanner)
and the head coil using identical
acquisition parameters to generate a
combined sensitivity map as described
inPapp et al. (2016).


# Units

```
As described in the Units, the specification of units SHOULD follow theInternational System of Units(SI, abbreviated from the French Système international (d’unités)).
TheCMIXF-12conventionforencodingunitsisRECOMMENDEDtoachievemaximumportabilityandlimitedvariabilityofrepresentation. IfaCMIXF-12representation
of a unit is not possible, the unit can be declared as custom units and defined in an accompanying JSON file, as described in the units section. Earlier versions of the BIDS
standard listed the following Unicode symbols, and these are still included for backwards compatibility:
```
1. U+03BC(μ)orU+00B5(μ)
2. U+03A9(Ω)orU+2126(Ω)
3. U+00B0(°)
Notethatforthefirsttwoentriesinthislist, twocharactersarepermissibleforeach, butthefirstcharacterineachentryispreferred, perUnicoderules(seethesectionon
”Duplicated Characters” on page 11 in theunicode report).

```
It is RECOMMENDED that units be CMIXF-12 compliant or among these five Unicode characters. Please note the appropriate upper- or lower- casing when using
CMIXF-12.
For cases that are unspecified by this appendix or the units section, theCMIXF-12convention applies.
You can use thecmixf Python packageto check whether your formatting is compliant.
Examples for CMIXF-12 (including the five unicode symbols mentioned above):
```
1. Different formatting of ”micro Volts”:
    (a)RECOMMENDED:uVorμV
    (b)NOT RECOMMENDED:microV,μvoltor1e-6V
2. Combinations of units:
    (a)RECOMMENDED:V/usfor theSlew rate
    (b)NOT RECOMMENDED:volts per microsecond

## Unit table


```
Unit name Unit symbol Quantity name
metre m length
kilogram kg mass
litre (liter) L volume
second s time
ampere A electric current
kelvin K thermodynamic temperature
mole mol amount of substance
candela cd luminous intensity
radian rad angle
steradian sr solid angle
hertz Hz frequency
newton N force, weight
pascal Pa pressure, stress
joule J energy, work, heat
watt W power, radiant flux
coulomb C electric charge or quantity of electricity
volt V voltage (electrical potential), emf
farad F capacitance
ohm Ohm resistance, impedance, reactance
siemens S electrical conductance
weber Wb magnetic flux
tesla T magnetic flux density
henry H inductance
degree Celsius oC temperature relative to 273.15 K
lumen lm luminous flux
lux lx illuminance
becquerel Bq radioactivity (decays per unit time)
gray Gy absorbed dose (of ionizing radiation)
sievert Sv equivalent dose (of ionizing radiation)
katal kat catalytic activity
```
### Prefixes

#### Multiples


```
Prefix name Prefix symbol Factor
deca da 101
hecto h 102
kilo k 103
mega M 106
giga G 109
tera T 1012
peta P 1015
exa E 1018
zetta Z 1021
yotta Y 1024
```
#### Submultiples

```
Prefix name Prefix symbol Factor
deci d 10-1
centi c 10-2
milli m 10-3
micro u 10-6
nano n 10-9
pico p 10-12
femto f 10-15
atto a 10-18
zepto z 10-21
yocto y 10-24
```

# Hierarchical Event Descriptors

HierarchicalEventDescriptors(HED)areacontrolledvocabularyoftermsdescribingeventsinamachine-actionableformsothatalgorithmscanusetheinformationwith-
outmanualrecoding. HEDannotationcanbeusedtodescribeanyexperimentaleventsbycombininginformationfromthedataset’s_events.tsvfilesand_events.json
sidecars.

## HED annotations and vocabulary

A HED annotation consists of terms selected from a controlled hierarchical vocabulary (the HED schema). Individual terms are comma-separated and may be grouped
using parentheses to indicate association. Seehttps://www.hedtags.org/display_hed.htmlto view the HED schema and theHED documentationfor additional resources.

Starting with HED version 8.0.0, HED allows users to annotate using individual terms or partial paths in the HED vocabulary (for exampleRedorVisual-presentation)
rather than the full paths in the HED hierarchy (Property/Sensory-property/Sensory-attribute/Visual-attribute/Color/CSS-color/Red-color/Red or
Property/Sensory-property/Sensory-presentation/Visual-presentation).

HED specific tools MUST treat the short and long HED tag forms interchangeably, converting between the forms when necessary, based on the HED schema. Examples
of test datasets using the various forms can be found inhed-examples/datasetson GitHub. Using the short form for tags is strongly RECOMMENDED whenever possible.

## Annotating events

Event-related data in BIDS appears in tab-separated value (events.tsv) files in various places in the dataset hierarchy (see Events).

events.tsvfiles MUST haveonsetanddurationcolumns. Dataset curators MAY also include additional columns and define their meanings in associated JSON sidecar
files (events.json).

Example: An excerpt from anevents.tsvfile containing three columns (trial_type,response_time, andstim_file) in addition to the requiredonsetandduration
columns.

onset duration trial_type response_time stim_file
1.2 0.6 go 1.435 images/red_square.jpg
5.6 0.6 stop 1.739 images/blue_square.jpg


Thetrial_typecolumn in the above example contains a limited number of distinct values (goandstop). This type of column is referred to as a categorical column, and
thecolumn’smeaningcanbeannotatedbyassigningHEDtagstodescribeeachofthesedistinctvalues. TheJSONsidecarprovidesaJSONobjectofannotationsforthese
categorical values. That is, the object is a dictionary mapping the categorical values to corresponding HED annotations.

In contrast, theresponse_timeandstim_filecolumns could potentially contain distinct values in every row. These columns are referred to as value columns and are
annotated by creating a HED tag string to describe a general pattern for these values. The HED annotation for a value column must include a#placeholder, which
dedicated HED tools MUST replace by the actual column value when the annotations are assembled for analysis.

Example: An accompanyingevents.jsonsidecar describing both categorical and value columns of the previous example. Thedurationcolumn is also annotated as a
value column.

{
"Duration":{
"LongName": "Image duration",
"Description":"Duration of the image presentations",
"Units":"s",
"HED": "Duration/# s"
},
"trial_type": {
"LongName": "Event category",
"Description":"Indicator of type of action that is expected",
"Levels":{
"go": "A red square is displayed to indicate starting",
"stop":"A blue square is displayed to indicate stopping"
},
"HED": {
"go": "Sensory-event, Visual-presentation, ((Square, Blue),(Computer-screen, Center-of))",
"stop":"Sensory-event, Visual-presentation, ((Square, Blue), (Computer-screen, Center-of))"
}
},
"response_time": {
"LongName":"Response time after stimulus",
"Description":"Time from stimulus presentation until subject presses button",
"Units": "ms",
"HED":"(Delay/# ms, Agent-action, (Experiment-participant, (Press, Mouse-button))),"
},
"stim_file": {
"LongName":"Stimulus filename",
"Description":"Relative path of the stimulus image file",
"HED":"Pathname/#"
}
}


Dedicated HED tools MUST assemble an annotation for each event by concatenating the annotations for each column.

Example: The fully assembled annotation for the first event in the aboveevents.tsvfile with onset1.2(the first row) is:

Duration/0.6 s, Sensory-event, Visual-presentation,
((Square, Blue), (Computer-screen, Center-of)),
(Delay/1.435 ms, Agent-action,
(Experiment-participant, (Press, Mouse-button))),
Pathname/images/red_square.jpg

### Annotation using the HED column

Another tagging strategy is to annotate individual events directly by including aHEDcolumn in theevents.tsvfile. This approach is necessary when each event has
annotations that are unique and do not fit into a standard set of patterns.

Some acquisition or presentation software systems directly write annotations during the experiment, and these MAY also be placed in theHEDcolumn of theevents.tsv
file.

DedicatedHED toolsthat assemblethe fullannotation forevents treatMUST notdistinguish betweenHED annotationsextracted from_events.jsonsidecarsand those
appearing in theHEDcolumn of_events.tsvfiles. The HED strings from all sources are concatenated to form the final event annotations.

Annotations placed in sidecars are the RECOMMENDED way to annotate data using HED. These annnotations are preferred to those placed directly in theHEDcolumn,
because they are simpler, more compact, more easily edited, and less prone to inconsistencies.

### HED and the BIDS inheritance principle

Moststudieshaveeventfileswhosecolumnscontaincategoricalandnumericalvaluesthataresimilaracrosstherecordingsinthestudy. Ifpossible,usersshouldannotate
these columns in a singleevents.jsonsidecar placed at the top level in the dataset.

If some recordings in the dataset have a column whose values deviate from a standard pattern, then the annotations for that column MUST be placed in sidecars located
deeper in the dataset directory hierarchy. According to the BIDS Inheritance Principle, once a column key in a sidecar (that is, the column name found in theevents.tsv
files) is set, information about that column cannot be overridden by a sidecar appearing in a directory closer to the dataset root.

### HED schema versions

The HED vocabulary is specified by a HED schema, which delineates the allowed HED path strings. The version of HED used in tagging a dataset should be provided in
theHEDVersionfieldofthedataset_description.jsonfilelocatedinthedatasetrootdirectory. ThisallowsforapropervalidationoftheHEDannotations(forexample
using thebids-validator).

Example: Thefollowingdataset_description.jsonfilespecifiesthattheHED8.1.0.xmlfilefromthehedxmldirectoryofthehed-specificationrepositoryonGitHub
should be used to validate the study event annotations.


##### {

"Name":"A great experiment",
"BIDSVersion": "1.7.0",
"HEDVersion": "8.1.0"
}

If you omit theHEDVersionfield from the dataset description file, any present HED information will be validated using the latest version of the HED schema. This is
bound to result in problems, and hence, it is strongly RECOMMENDED that theHEDVersionfield be included when using HED in a BIDS dataset.

#### Using HED library schemas

HED also allows you to use one or more specialized vocabularies along with or instead of the standard vocabulary. These specialized vocabularies are developed by
communities of users and are available in the GitHubhed-schema-libraryrepository. Library schema are specified in the form<library-name<_>library-version>.

Example: The followingdataset_description.jsonfile specifies that theHED8.1.0.xmlstandard schema should be used along with the SCORE library for clinical
neurological annotation and a test library. These later schemas are located atHED_score_0.0.1.xmlandHED_testlib_1.0.2.xml, respectively.

{
"Name":"A great experiment",
"BIDSVersion": "1.7.0",
"HEDVersion": ["8.1.0","sc:score_0.0.1","ts:testlib_1.0.2"]
}

Thesc:andts:are user-chosen prefixes used to distinguish the sources of the terms in the HED annotation. These prefixes MUST be alphanumeric.

ThefollowingHEDannotationfromthisdatasetusesthesc:prefixwithPhotomyogenic-responseandWicket-spikesbecausethesetermsarefromtheSCORElibrary,
whileData-featureis from the standard HED schema.

Data-feature, sc:Photomyogenic-response, sc:Wicket-spikes

If only one schema is being used for annotation, the prefix can be omitted entirely. The followingdataset_description.jsonindicates that only the SCORE library
version 0.0.1 will be used for HED annotation in this dataset.

{
"Name":"A great experiment",
"BIDSVersion": "1.7.0",
"HEDVersion": "score_0.0.1"
}

The corresponding notations in the dataset do not have a prefix:

Photomyogenic-response, Wicket-spikes


# MEG file formats

Each MEG system brand has specific file organization and data formats. RECOMMENDED values formanufacturer_specific_extensions:

Value Description

ctf CTF (directory with.dsextension)
fif Neuromag / Elekta / MEGIN and BabyMEG (file with extension.fif)
4d BTi / 4D Neuroimaging (directory containing multiple files without extensions)
kit KIT / Yokogawa / Ricoh (file with extension.sqd,.con,.raw,.aveor.mrk)
kdf KRISS (file with extension.kdf)
itab Chieti system (file with extension.rawand.mhd)

Below are specifications for each system brand.

## CTF

Each experimental run with a CTF system yields a directory with a.dsextension, containing several files. The OPTIONAL digitized positions of the head points are
usually stored in a separate.posfile, not necessarily within the.dsdirectory.

[sub-<label>[_ses-<label>]_headshape.pos]
sub-<label>[_ses-<label>]_task-<label>[_run-<index>]_meg.ds>

CTF’s data storage is therefore via directories containing multiple files. The files contained within a.dsdirectory are named such that they match the parent directory,
but preserve the original file extension (for example,.meg4,.res4). The renaming of CTF datasets SHOULD be done with a specialized software such as the CTF newDs
command-line application orMNE-BIDS.

Example:

```
sub-control01/
ses-001/
```

```
sub-control01_ses-001_scans.tsv
meg/
sub-control01_ses-001_coordsystem.json
sub-control01_ses-001_headshape.pos
sub-control01_ses-001_task-rest_run-01_meg.ds/
sub-control01_ses-001_task-rest_run-01_meg.json
sub-control01_ses-001_task-rest_run-01_channels.tsv
```
To learn more about CTF’s data organization:https://www.fieldtriptoolbox.org/getting_started/ctf

### Neuromag/Elekta/MEGIN

Neuromag/Elekta/MEGIN and Tristan Technologies BabyMEG data is stored as FIFF files with the extension.fif. The digitized positions of the head points are saved
inside the FIFF file along with the MEG data, with typically no_headshapefile.

sub-<label>[_ses-<label>]_task-<label>[_run-<index>]_meg.fif

#### Cross-talk and fine-calibration files

In case internal active shielding (IAS) was used during acquisition, raw FIFF files need to be processed using Maxwell filtering (signal-space separation, SSS) to make the
datausable. Tothisend, twospecificfilesareneeded: Thecross-talkfile, andthefine-calibrationfile, bothofwhichareproducedbytheMaxFiltersoftwareandthework
of the Neuromag/Elekta/MEGIN engineers during maintenance of the MEG acquisition system. Both files are thus specific to the site of recording and may change in the
process of regular system maintenance.

In BIDS, the cross-talk and fine-calibration files are shared unmodified, including their original extensions (.fiffor cross-talk and.datfor fine-calibration), but with
BIDS file naming convention and by using theacqentity.

- cross-talk file template:sub-<label>[_ses-<label>]_acq-crosstalk_meg.fif
- fine-calibration file template:sub-<label>[_ses-<label>]_acq-calibration_meg.dat

Note that cross-talk files MUST be denoted usingacq-crosstalkand fine-calibration files MUST be denoted usingacq-calibration.

Thecross-talkandfine-calibrationdataMUSTbestoredinthesubject-levelmegdirectory,whichmaybenestedinsideases-<label>directory,asshowninthefollowing
examples.

Example with single session (omitted session directory)

```
sub-01/
meg/
sub-01_coordsystem.json
sub-01_task-rest_meg.fif
sub-01_task-rest_meg.json
sub-01_task-rest_channels.tsv
```

```
sub-01_acq-crosstalk_meg.fif
sub-01_acq-calibration_meg.dat
sub-02/
meg/
sub-02_coordsystem.json
sub-02_task-rest_meg.fif
sub-02_task-rest_meg.json
sub-02_task-rest_channels.tsv
sub-02_acq-crosstalk_meg.fif
sub-02_acq-calibration_meg.dat
```
Example with multiple sessions

```
sub-01/
ses-01/
sub-01_ses-01_scans.tsv
meg/
sub-01_ses-01_coordsystem.json
sub-01_ses-01_task-rest_run-01_meg.fif
sub-01_ses-01_task-rest_run-01_meg.json
sub-01_ses-01_task-rest_run-01_channels.tsv
sub-01_ses-01_acq-crosstalk_meg.fif
sub-01_ses-01_acq-calibration_meg.dat
ses-02/
sub-01_ses-02_scans.tsv
meg/
sub-01_ses-02_coordsystem.json
sub-01_ses-02_task-rest_run-01_meg.fif
sub-01_ses-02_task-rest_run-01_meg.json
sub-01_ses-02_task-rest_run-01_channels.tsv
sub-01_ses-02_acq-crosstalk_meg.fif
sub-01_ses-02_acq-calibration_meg.dat
```
#### Sharing FIFF data after signal-space separation (SSS)

After applying SSS (for example, by using the MaxFilter software), files SHOULD be renamed with the corresponding label (for example,proc-sss) and placed in a
derivativessubdirectory.

Example:

```
sub-control01/
ses-001/
```

```
meg/
sub-control01_ses-001_task-rest_run-01_proc-sss_meg.fif
sub-control01_ses-001_task-rest_run-01_proc-sss_meg.json
```
#### Split files

In the case of long data recordings that exceed a file size of 2Gb, the.fiffiles are conventionally split into multiple parts. For example:

some_file.fif
some_file-1.fif

Each of these files has an internal pointer to the next file. This is important when renaming these split recordings to the BIDS convention. Instead of a simple renaming,
files should be read in and saved under their new names with dedicated tools likeMNE, which will ensure that not only the filenames, but also the internal file pointers
will be updated.

It is RECOMMENDED that FIFF files with multiple parts use thesplit-<index>entity to indicate each part.

If there are multiple parts of a recording and the optionalscans.tsvis provided, remember to list all files separately inscans.tsvand that the entries for theacq_time
column inscans.tsvMUST all be identical, as described in Scans file.

Example:

```
sub-control01/
ses-001/
meg/
sub-control01_ses-001_task-rest_run-01_split-01_meg.fif
sub-control01_ses-001_task-rest_run-01_split-02_meg.fif
```
More information can be found under the following links:

- Neuromag/Elekta/MEGIN data organization
- BabyMEG

#### Recording dates in .fif files

Itisimportanttonotethatrecordingdatesin.fiffilesarerepresentedasint32formatsecondssince(orbefore)theEpoch(1970-01-01T00:00:00.000000UTC).Integers
inint32format can encode values from -2,147,483,647 to +2,147,483,647. Due to this representation, the Neuromag/Elekta/MEGIN file format for MEG (.fif) does not
support recording dates earlier than1901-12-13T08:45:53.000000UTC or later than2038-01-19T03:14:07.000000UTC.

### BTi/4D neuroimaging

Each experimental run on a 4D neuroimaging/BTi system results in a directory containing multiple files without extensions.

[sub-<label>[_ses-<label>]_headshape.pos]
sub-<label>[_ses-<label>]_task-<label>[_run-<index>]_meg>


```
One SHOULD rename/create a parent run-specific directory and keep the original files for each run inside (for example,c,rfhp0.1Hz,configandhs_file).
Example:
sub-control01/
ses-001/
sub-control01_ses-001_scans.tsv
meg/
sub-control01_ses-001_coordsystem.json
sub-control01_ses-001_headshape.pos
sub-control01_ses-001_task-rest_run-01_meg/
sub-control01_ses-001_task-rest_run-01_meg.json
sub-control01_ses-001_task-rest_run-01_channels.tsv
```
Where:

```
sub-control01_ses-001_task-rest_run-01_meg/
config
hs_file
e,rfhp1.0Hz.COH
c,rfDC
More about the 4D neuroimaging/BTi data organization at:https://www.fieldtriptoolbox.org/getting_started/bti
```
### KIT/Yokogawa/Ricoh

```
Each experimental run on a KIT/Yokogawa/Ricoh system yields a raw file with either.sqdor.conextension, and with its associated marker coil file(s) with either.sqd
or.mrkextension. The marker coil file(s) contain coil positions in the acquisition system’s native space. Head points and marker points in head space are acquired using
third-party hardware.
Example:
sub-control01/
ses-001/
sub-control01_ses-001_scans.tsv
meg/
sub-control01_ses-001_coordsystem.json
sub-control01_ses-001_headshape.txt
sub-control01_ses-001_task-rest_run-01_meg
sub-control01_ses-001_task-rest_run-01_meg.json
sub-control01_ses-001_task-rest_run-01_channels.tsv
sub-control01_ses-001_task-rest[_acq-<label>]_run-01_markers.<mrk,sqd>
sub-control01_ses-001_task-rest_run-01_meg.<con,sqd>
```

To understand why both.sqdand.con, as well as both.sqdand.mrkare valid extensions, we provide a brief historical perspective on the evolution of the data format:
TheoriginalextensionforKIT/Yokogawa/Ricohcontinuousdatawas.sqd. Thiswaslatermodernizedto.con(todenote”continuous”). However,topreservebackwards
compatibility,.sqdis still a valid extension for the raw, continuous data file. The original extension for KIT/Yokogawa/Ricoh marker files was.sqdas well. That lead
to the ambiguous situation where both the raw data and the marker file(s) could end on.sqd. To distinguish between continuous data and marker file(s), the internal
header of the files needed to be read first. For this reason, the marker file extension was later modernized to.mrkto better disambiguate files. However again, to preserve
backwards compatibility,.sqdis still a valid extension for the marker file(s).

If there are multiple files with marker coils, the marker files must have theacq-<label>entity and no more that two marker files may be associated with one raw data
file. While the acquisition entity can take any value, it is RECOMMENDED that if the two marker measurements occur before and after the raw data acquisition,pre
andpostare used to differentiate the two situations.

More about the KIT/Yokogawa/Ricoh data organization at:https://www.fieldtriptoolbox.org/getting_started/yokogawa

### KRISS

EachexperimentalrunontheKRISSsystemproducesafilewithextension.kdf. Additionalfilescanbeavailableinthesamedirectory: thedigitizedpositionsofthehead
points (\_digitizer.txt), the position of the center of the MEG coils (.chn) and the event markers (.trg).

[sub-<label>[_ses-<label>]_headshape.txt]
sub-<label>[_ses-<label>]_task-<label>[_run-<index>]_meg.kdf
sub-<label>[_ses-<label>]_task-<label>[_run-<index>]_meg.chn
sub-<label>[_ses-<label>]_task-<label>[_run-<index>]_meg.trg
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>]_digitizer.txt

Example:

```
sub-control01/
ses-001/
sub-control01_ses-001_scans.tsv
meg/
sub-control01_ses-001_coordsystem.json
sub-control01_ses-001_headshape.txt
sub-control01_ses-001_task-rest_run-01_meg
sub-control01_ses-001_task-rest_run-01_meg.json
sub-control01_ses-001_task-rest_run-01_channels.tsv
sub-control01_ses-001_task-rest_run-01_meg.chn
sub-control01_ses-001_task-rest_run-01_meg.kdf
sub-control01_ses-001_task-rest_run-01_meg.trg
sub-control01_ses-001_task-rest_digitizer.txt
```

### ITAB

EachexperimentalrunonaITAB-ARGOS153systemyieldsaraw(.raw)datafileplusanassociatedbinaryheaderfile(.mhd). TherawdatafilehasanASCIIheaderthat
contains detailed information about the data acquisition system, followed by binary data. The associated binary header file contains part of the information from the
ASCII header, specifically the one needed to process data, plus other information on offline preprocessing performed after data acquisition (for example, sensor position
relative to subject’s head, head markers, stimulus information).

Example:

```
sub-control01/
ses-001/
meg/
sub-control01_ses-001_coordsystem.json
sub-control01_ses-001_headshape.txt
sub-control01_ses-001_task-rest_run-01_meg
sub-control01_ses-001_task-rest_run-01_meg.json
sub-control01_ses-001_task-rest_run-01_channels.tsv
sub-control01_ses-001_task-rest_run-01_meg.raw
sub-control01_ses-001_task-rest_run-01_meg.raw.mhd
```
### Aalto MEG–MRI

For stand-alone MEG data, the Aalto hybrid device uses the standard.fifdata format and follows the conventions of Elekta/Neuromag as described above. The.fif
files may contain unreconstructed MRI data. The inclusion of MRI data and information for accurate reconstruction will be fully standardized at a later stage.


# MEG systems

Preferred names of MEG systems comprise restricted keywords for Manufacturer field in the*_meg.jsonfile:

- CTF
- Neuromag/Elekta/Megin
- BTi/4D
- KIT/Yokogawa/Ricoh
- KRISS
- ITAB
- Aalto/MEG-MRI
- Other

Restricted keywords for ManufacturersModelName field in the*_meg.jsonfile:

```
System Model Name Manufacturer Details
CTF-64 CTF
CTF-151 CTF https://www.ctf.com/products
CTF-275 CTF CTF-275: OMEGA 2000
Neuromag-122 Neuromag/Elekta/Megin
ElektaVectorview Neuromag/Elekta/Megin 102 magnetometers + 204 planar gradiometers
ElektaTRIUX Neuromag/Elekta/Megin https://www.elekta.com/diagnostic-solutions/
4D-Magnes-WH2500 BTi/4D
4D-Magnes-WH3600 BTi/4D
KIT-157 KIT/Yokogawa
KIT-160 KIT/Yokogawa
KIT-208 KIT/Yokogawa
ITAB-ARGOS153 ITAB
Aalto-MEG-MRI-YYYY/MM Aalto/MEG-MRI YYYY-MM (year, month; or major version)
```

# Coordinate systems

## Introduction

To interpret a coordinate (x, y, z), it is required that you know (1) relative to which origin the coordinate is expressed, (2) the interpretation of the three axes, and (3) the
units in which the numbers are expressed. This information is sometimes called the coordinate system.

These letters help describe the coordinate system definition:

- A/P means anterior/posterior
- L/R means left/right
- S/I means superior/inferior

For example:RASmeans that the first dimension (X) points towards the right hand side of the head, the second dimension (Y) points towards the Anterior aspect of the
head,andthethirddimension(Z)pointstowardsthetopofthehead. Thedirectionsareconsideredtobefromthesubject’sperspective. Forexample,intheRAScoordinate
system, a point to the subject’s left will have a negativexvalue.

Besidescoordinatesystems,definedbytheiroriginanddirectionoftheaxes,BIDSdefines”spaces”asanartificialframeofreference,createdtodescribedifferentanatomies
in a unifying manner (see for example,doi:10.1016/j.neuroimage.2012.01.024).

The ”space” and all coordinates expressed in this space are by design a transformation of the real world geometry, and nearly always different from the individual
subject space that it stems from. An example is the Talairach-Tournoux space, which is constructed by piecewise linear scaling of an individual’s brain to that of the
Talairach-Tournoux 1988 atlas. In the Talairach-Tournoux space, the origin of the coordinate system is at the AC and units are expressed in mm.

The coordinate systems below all relate to neuroscience and therefore to the head or brain coordinates. Please be aware that all data acquisition starts with ”device
coordinates” (scanner), which does not have to be identical to the initial ”file format coordinates” (DICOM), which are again different from the ”head” coordinates (for
example, NIFTI). Not only do device coordinate vary between hardware manufacturers, but also the head coordinates differ, mostly due to different conventions used in
specific software packages developed by different (commercial or academic) groups.


### Coordinate Systems applicable to MEG, EEG, and iEEG

Generally, across the MEG, EEG, and iEEG modalities, the first two pieces of information for a coordinate system (origin and orientation) are specified in
<CoordSysType>CoordinateSystem. The third piece of information for a coordinate system (units) are specified in<CoordSysType>CoordinateUnits. Here,
<CoordSysType>can be one of the following, depending on the data that is supposed to be documented:

- MEG
- EEG
- iEEG
- Fiducials
- AnatomicalLandmark
- HeadCoil
- DigitizedHeadPoints

Allowed values for the<CoordSysType>CoordinateSystemfield come from a list of restricted keywords, as listed in the sections below.

Note thatFiducials,AnatomicalLandmark,HeadCoil, andDigitizedHeadPoints CoordSysTypes share the restricted keywords with the data modality they are shared
with. For example, if anAnatomicalLandmarkfield is shared as part of an EEG dataset, the EEG-specific coordinate systems apply. However, if it is shared as part of an
MEG dataset, the MEG-specific coordinate systems apply.

If no value from the list of restricted keywords fits, there is always the option to specify the value as follows:

- Other: Use this for other coordinate systems and specify all required details in the<CoordSysType>CoordinateSystemDescriptionfield

If you believe a specific coordinate system should be added to the list of restricted keywords for MEG, EEG, or iEEG, please open a new issue on thebids-standard/bids-
specification GitHub repository.

Note that the short descriptions below may not capture all details. For detailed descriptions of the coordinate systems below, please see theFieldTrip webpage.

#### Commonly used anatomical landmarks in MEG, EEG, and iEEG research

In the documentation below we refer to anatomical landmarks such as the Left Pre Auricular point (LPA) and the Right Pre Auricular point (RPA), or the left and right
Helix-Tragus Junction (LHJ, RHJ).

These anatomical landmarks are commonly used in MEG, EEG, and iEEG research to define coordinate systems that capture digitized sensor positions.

More information can be obtained from the FieldTrip webpage.

- FAQ: LPA and RPA
- FAQ: Beyond LPA and RPA

#### MEG Specific Coordinate Systems

Restricted keywords for the<CoordSysType>CoordinateSystemfield in thecoordinatesystem.jsonfile for MEG datasets:

- CTF: ALS orientation and the origin between the ears


- ElektaNeuromag: RAS orientation and the origin between the ears
- 4DBti: ALS orientation and the origin between the ears
- KitYokogawa: ALS orientation and the origin between the ears
- ChietiItab: RAS orientation and the origin between the ears
- Any keyword from the list of Standard template identifiers: RAS orientation and the origin at the center of the gradient coil for template NifTI images

In the case that MEG was recorded simultaneously with EEG, the restricted keywords for EEG specific coordinate systems can also be applied to MEG:

- CapTrak
- EEGLAB
- EEGLAB-HJ

#### EEG Specific Coordinate Systems

Restricted keywords for the<CoordSysType>CoordinateSystemfield in thecoordsystem.jsonfile for EEG datasets:

- CapTrak: RAS orientation and the origin approximately between LPA and RPA
- EEGLAB: ALS orientation and the origin exactly between LPA and RPA. For more information, see theEEGLAB wiki page.
- EEGLAB-HJ: ALS orientation and the origin exactly between LHJ and RHJ. For more information, see theEEGLAB wiki page.
- Any keyword from the list of Standard template identifiers: RAS orientation and the origin at the center of the gradient coil for template NifTI images

In the case that EEG was recorded simultaneously with MEG, the restricted keywords for MEG specific coordinate systems can also be applied to EEG:

- CTF
- ElektaNeuromag
- 4DBti
- KitYokogawa
- ChietiItab

#### iEEG Specific Coordinate Systems

Restricted keywords for the<CoordSysType>CoordinateSystemfield in thecoordsystem.jsonfile for iEEG datasets:

- Pixels: If electrodes are localized in 2D space (only x and y are specified and z is n/a), then the positions in this file must correspond to the locations expressed in
    pixelsonthephoto/drawing/renderingoftheelectrodesonthebrain. Inthiscase, coordinatesmustbe(row,column)pairs, with(0,0)correspondingtotheupperleft
    pixel and (N,0) corresponding to the lower left pixel.
- ACPC: The origin of the coordinate system is at the Anterior Commissure and the negative y-axis is passing through the Posterior Commissure. The positive z-axis
    is passing through a mid-hemispheric point in the superior direction. The anatomical landmarks are determined in the individual’s anatomical scan and no scaling
    or deformations have been applied to the individual’s anatomical scan. For more information, see theACPC siteon the FieldTrip toolbox wiki.
- ScanRAS: The origin of the coordinate system is the center of the gradient coil for the corresponding T1w image of the subject, and the x-axis increases left to right,
    the y-axis increases posterior to anterior and the z-axis increases inferior to superior. For more information see theNipy Documentation. It is strongly encouraged


```
to align the subject’s T1w to ACPC so that theACPCcoordinate system can be used. If the subject’s T1w in the BIDS dataset is not aligned to ACPC,ScanRASshould
be used.
```
- Any keyword from the list of Standard template identifiers: RAS orientation and the origin at the center of the gradient coil for template NifTI images

### Image-based Coordinate Systems

Thetransformationoftherealworldgeometrytoanartificialframeofreferenceisdescribedin<CoordSysType>CoordinateSystem. Unlessotherwisespecifiedbelow,the
originisattheACandtheorientationoftheaxesisRAS.Unlessspecifiedexplicitlyinthesidecarfileinthe<CoordSysType>CoordinateUnitsfield,theunitsareassumed
to be mm.

#### Standard template identifiers

Coordinate System Description Used by Reference

ICBM452AirSpace Reference space defined by the
”average of 452 T1-weighted MRIs of
normal young adult brains” with
”linear transforms of the subjects into
the atlas space using a 12-parameter
affine transformation”

```
https://www.loni.usc.edu/research/atlases
```
ICBM452Warp5Space Reference space defined by the
”average of 452 T1-weighted MRIs of
normal young adult brains” ”based on a
5th order polynomial transformation
into the atlas space”

```
https://www.loni.usc.edu/research/atlases
```
IXI549Space Reference space defined by the average
of the ”549 (...) subjects from the IXI
dataset” linearly transformed to ICBM
MNI 452.

```
SPM12 https://brain-development.org/
```
fsaverage Thefsaverageis a dual template
providing both volumetric and surface
coordinates references. The volumetric
template corresponds to a FreeSurfer
variant ofMNI305space. The
fsaverageatlas also defines a surface
reference system (formerly described as
fsaverage[3|4|5|6|sym]).

```
Freesurfer
```

Coordinate System Description Used by Reference

fsaverageSym Thefsaverageis a dual template
providing both volumetric and surface
coordinates references. The volumetric
template corresponds to a FreeSurfer
variant ofMNI305space. The
fsaverageSymatlas also defines a
symmetric surface reference system
(formerly described asfsaveragesym).

```
Freesurfer
```
fsLR ThefsLRis a dual template providing
both volumetric and surface
coordinates references. The volumetric
template corresponds to
MNI152NLin6Asym. Surface templates
are given at several sampling densities:
164k (used by HCP pipelines for 3T and
7T anatomical analysis), 59k (used by
HCP pipelines for 7T MRI bold and
DWI analysis), 32k (used by HCP
pipelines for 3T MRI bold and DWI
analysis), or 4k (used by HCP pipelines
for MEG analysis) fsaverage_LR
surface reconstructed from the T1w
image.

```
Freesurfer
```
MNIColin27 Average of 27 T1 scans of a single
subject

SPM96 https://www.bic.mni.mcgill.ca/Services
Atlases/Colin27Highres
MNI152Lin Also known as ICBM (version with
linear coregistration)

SPM99 to SPM8 https://www.bic.mni.mcgill.ca/Services
Atlases/ICBM152Lin
MNI152NLin2009[a-c][Sym|Asym] Also known as ICBM (non-linear
coregistration with 40 iterations,
released in 2009). It comes in either
three different flavours each in
symmetric or asymmetric version.

```
DARTEL toolbox in SPM12b https://www.bic.mni.mcgill.ca/Services
Atlases/ICBM152NLin2009
```
MNI152NLin6Sym Also known as symmetric ICBM 6th
generation (non-linear coregistration).

FSL https://www.bic.mni.mcgill.ca/Services
Atlases/ICBM152NLin6
MNI152NLin6ASym A variation ofMNI152NLin6Symbuilt by
A. Janke that is released as the MNI
template of FSL. Volumetric templates
included withHCP-Pipelines
correspond to this template too.

```
HCP-Pipelines doi:10.1016/j.neuroimage.2012.01.024
```

Coordinate System Description Used by Reference

MNI305 Also known as avg305.
NIHPD Pediatric templates generated from the
NIHPD sample. Available for different
age groups (4.5–18.5 y.o., 4.5–8.5 y.o.,
7–11 y.o., 7.5–13.5 y.o., 10–14 y.o.,
13–18.5 y.o. This template also comes in
either -symmetric or -asymmetric
flavor.

```
https://www.bic.mni.mcgill.ca/Services
Atlases/NIHPD-obj1
```
OASIS30AntsOASISAnts https://figshare.com/articles/ANTs_A
NTsR_Brain_Templates/915436
OASIS30Atropos https://mindboggle.info/data.html
Talairach Piecewise linear scaling of the brain is
implemented as described in TT88.

```
http://talairach.org/
```
UNCInfant Infant Brain Atlases from Neonates to
1- and 2-year-olds.

```
https:
//www.nitrc.org/projects/pediatricatlas
```
The following template identifiers are retained for backwards compatibility of BIDS implementations. However, their use is DEPRECATED.

```
Coordinate System Description RECOMMENDED alternative identifier
fsaverage[3|4|5|6|sym] Images were sampled to the FreeSurfer surface
reconstructed from the subject’s T1w image, and
registered to an fsaverage template
```
```
fsaverage[Sym]
```
```
UNCInfant[0|1|2]V[21|22|23] Infant Brain Atlases from Neonates to 1- and
2-year-olds.
https://www.nitrc.org/projects/pediatricatlas
```
```
UNCInfant
```
#### Nonstandard coordinate system identifiers

ThefollowingtemplateidentifiersareRECOMMENDEDforindividual-andstudy-specificreferencespaces. Inorderforthesespacestobeinterpretable,SpatialReference
metadata MUST be provided, as described in Common file level metadata fields.

In the case of multiple study templates, additional names may need to be defined.


Coordinate System Description

individual Participant specific anatomical space (for example derived from T1w and/or T2w
images). This coordinate system requires specifying an additional,
participant-specific file to be fully defined. In context of surfaces this space has
been referred to asfsnative.
study Custom space defined using a group/study-specific template. This coordinate
system requires specifying an additional file to be fully defined.

#### Non-template coordinate system identifiers

Thescannercoordinatesystemisimplicitandassumedbydefaultifthederivativefilenamedoesnotdefineanyspace-<label>. Pleasenotethatspace-scannerSHOULD
NOT be used, it is mentioned in this specification to make its existence explicit.

Coordinate System Description

scanner The intrinsic coordinate system of the original image (the first entry of
RawSources) after reconstruction and conversion to NIfTI or equivalent for the
case of surfaces and dual volume/surface files.


# Quantitative MRI

QuantitativeMRI(qMRI)isacollectionofmethodsaimingatgeneratingparametricmapsthatcancharacterizeunderlyingtissueproperties. Unlikethoseofconventional
MRimages(forexample,T1worT2w),intensityvaluesofquantitativemapsarenotrepresentedinanarbitraryrange. Instead,thesemapsarerepresentedeitherinabsolute
physical units (for example,secondsforT1map), or within an application dependent range of arbitrary units (for example, myelin water fractionMWFmapin brain).

## Organization of qMRI data in BIDS

UnlikeconventionalMRimages,quantitativemapsarenotimmediateproductsoftheimagereconstructionstep(fromk-spacedatatostructuralimages). Intensityvalues
of qMRI maps are calculated by fitting a collection of parametrically linked images to a biophysical model or to an MRI signal representation. This processing is typically
carried out in the image domain. There are two main ways to obtain a quantitative map:

1. Pre-generated qMRI maps: The qMRI maps are generated right after the reconstruction of required input images and made available to the user at the scanner
    console. The acquisition scenarios may include (a) vendor pipelines or (b) open-source pipelines deployed at the scanner site.
2. Post-generated qMRI maps: The qMRI maps are generated from a collection of input data after they are exported from the scanner site. This type of processing is
    commonly carried out using an open-source software such ashMRI toolbox,mrQ,PyQMRI,qmap,qMRLab, andQUIT.

#### Inputs are file collections

The common concept of entity-linked file collections enables the description of a qMRI application by creating logical groups of input files throughsuffixand certain
entities representing acquisition parameters (echo,flip,inv,mt) or file parts (part).

If a qMRI file collection is intended for creating structural quantitative maps (for example,T1map), files belonging to that collection are stored in theanatsubdirectory.
Below is an example file collection forMP2RAGE:

```
sub-01/
anat/
sub-01_inv-1_part-mag_MP2RAGE.nii.gz
sub-01_inv-1_part-phase_MP2RAGE.nii.gz
sub-01_inv-1_MP2RAGE.json
sub-01_inv-2_part-mag_MP2RAGE.nii.gz
```

```
sub-01_inv-2_part-phase_MP2RAGE.nii.gz
sub-01_inv-2_MP2RAGE.json
```
Commonly,RFfieldmaps(B1+andB1-maps)areusedforthecorrectionofstructuralquantitativemaps. Astheseimagesdonotconveysubstantialstructuralinformation,
respective file collections of RF fieldmaps are stored in thefmapsubdirectory. Below is an example file collection for RF transmit field mapTB1EPI:

```
sub-01/
fmap/
sub-01_echo-1_flip-1_TB1EPI.nii.gz
sub-01_echo-1_flip-1_TB1EPI.json
sub-01_echo-2_flip-1_TB1EPI.nii.gz
sub-01_echo-2_flip-1_TB1EPI.json
sub-01_echo-1_flip-2_TB1EPI.nii.gz
sub-01_echo-1_flip-2_TB1EPI.json
sub-01_echo-2_flip-2_TB1EPI.nii.gz
sub-01_echo-2_flip-2_TB1EPI.json
```
Please visit the file collections appendix to see the list of currently supported qMRI applications.

#### Quantitative maps are derivatives

Regardlessofhowtheyareobtained(pre-orpost-generated),qMRImapsarestoredinthederivativesdirectory. ForexampleaT1mapcanbegeneratedfromanMP2RAGE
file collection using either options.

If the map is post-generated:

```
ds-example/
derivatives/
qMRI-software-name/
sub-01/
anat/
sub-01_T1map.nii.gz
sub-01_T1map.json
sub-01_UNIT1.nii.gz
sub-01_UNIT1.json
```
If the map is pre-generated, for example, by a Siemens scanner:

```
ds-example/
derivatives/
Siemens/
sub-01/
anat/
sub-01_T1map.nii.gz
```

```
sub-01_T1map.json
sub-01_UNIT1.nii.gz
sub-01_UNIT1.json
Note: Eventhoughtheprocessfromwhichpre-generatedqMRImapsareobtained(vendorpipelines)isnotknown,vendorsgenerallyallowexportingofthecorresponding
input data. It is RECOMMENDED to share them along with the vendor outputs, whenever possible for a qMRI method supported by BIDS.
```
#### Example datasets

```
You can find example file collections and qMRI maps organized according to BIDS in theBIDS examples.
```
### Metadata requirements for qMRI data

```
The table of required entities for qMRI file collections are provided in the entity table. However, viability of a qMRI file collection is determined not only by the naming
and organization of the input files, but also by which metadata fields are provided in accompanying json files.
```
#### Method-specific priority levels for qMRI file collections

```
Anatomy imaging data
```
```
File collection REQUIRED metadata OPTIONAL metadata
VFA FlipAngle,PulseSequenceType,
RepetitionTimeExcitation
```
```
SpoilingRFPhaseIncrement
```
```
IRT1 InversionTime
MP2RAGE* FlipAngle,InversionTime,
RepetitionTimeExcitation,
RepetitionTimePreperation,
NumberShots,MagneticFieldStrength
```
```
EchoTime
```
```
MESE EchoTime
MEGRE EchoTime
MTR MTState
MTS FlipAngle,MTState,RepetitionTimeExcitation
MPM FlipAngle,MTState,RepetitionTimeExcitation EchoTime
```
* Please see MP2RAGE-specific notes for the calculation ofNumberShotsand regarding the organization ofUNIT1image.

```
Explanation of the table:
```
- The metadata fields listed in the REQUIRED column are needed to perform a minimum viable qMRI processing for the correspondingfile collection.


- Note that some of the metadata fields may be constant across different files in a file collection, yet still required as an input (for example,NumberShotsinMP2RAGE).
    Such metadata fields MUST be provided in the accompanying JSON files.
- ThemetadatafieldslistedintheOPTIONALcolumncanbeusedtoformdifferentflavorsofanexistingfilecollectionsuffix,dispensingwiththeneedforintroducing
    a new suffix. See deriving the intended qMRI application from an ambiguous file collection for details.

```
Field maps
```
```
File collection REQUIRED metadata
TB1DAM FlipAngle
TB1EPI EchoTime,FlipAngle,TotalReadoutTime,MixingTime
TB1AFI RepetitionTime
TB1TFL
TB1RFM
TB1SRGE* FlipAngle,InversionTime,RepetitionTimeExcitation,
RepetitionTimePreperation,NumberShots
RB1COR
```
* Please see TB1SRGE-specific notes for the calculation ofNumberShots.

#### Metadata requirements for qMRI maps

```
As qMRI maps are stored as derivatives, they are subjected to the metadata requirements of derived datasets.
An exampledataset_description.jsonfor a qMRI map derivatives directory:
ds-example/
derivatives/
qMRLab/
dataset_description.json
sub-01/
anat/
sub-01_T1map.nii.gz
sub-01_T1map.json
sub-01_M0map.nii.gz
sub-01_M0map.json
dataset_description.json:
{
"Name": "qMRLab Outputs",
```

"BIDSVersion": "1.5.0",
"DatasetType": "derivative",
"GeneratedBy": [
{
"Name": "qMRLab",
"Version": "2.4.1",
"Container": {
"Type": "docker",
"Tag": "qmrlab/minimal:2.4.1"
}
},
{
"Name": "Manual",
"Description": "Generated example T1map outputs"
}
],
"SourceDatasets": [
{
"DOI": "DOI 10.17605/OSF.IO/K4BS5",
"URL": "https://osf.io/k4bs5/",
"Version": "1"
}
]
}

In addition to the metadata fields provided in thedataset_description.json, qMRI maps are RECOMMENDED to be accompanied by sidecar JSON files that contain
further information about the quantified maps. Although this may not be the generic case for common derivative outputs, a proper interpretation of qMRI maps may
critically depend on some metadata fields. For example, without the information ofMagneticFieldStrength, white-matter T1 values in aT1mapbecome elusive.

- All the acquisition parameters that are constant across the files in a file collection are RECOMMENDED to be added to the sidecar json of the qMRI maps.
- Relevant acquisition parameters that vary across files in a qMRI file collection are RECOMMENDED to be added to the sidecar json of the qMRI map in array form.
- The JSON file accompanying a qMRI map which is obtained by using open-source software is RECOMMENDED to include additional metadata fields listed in the
    following table:


Key name Requirement Level Data type Description

Sources RECOMMENDED arrayofstrings A list of files with the paths specified
using Sources; these files were directly
used in the creation of this derivative
data file. For example, if a derivative A
is used in the creation of another
derivative B, which is in turn used to
generate C in a chain of A->B->C, C
should only list B in"Sources", and B
should only list A in"Sources".
However, in case both X and Y are
directly used in the creation of Z, then Z
should list X and Y in"Sources",
regardless of whether X was used to
generate Y. Using paths specified
relative to the dataset root is Sources.
EstimationReference RECOMMENDED string Reference to the study/studies on which
the implementation is based.
EstimationAlgorithm RECOMMENDED string Type of algorithm used to perform
fitting (for example,"linear",
"non-linear","LM"and such).
Units RECOMMENDED string Measurement units for the associated
file. SI units in CMIXF formatting are
RECOMMENDED (see Units).
BasedOn BasedOn stringorarrayofstrings List of files in a file collection to
generate the map. Fieldmaps are also
listed, if involved in the processing.
This field is DEPRECATED, and this
metadata SHOULD be recorded in the
Sourcesfield using BasedOn to
distinguish sources from different
datasets.

Example:

sub-01_T1map.nii.gz
sub-01_T1map.json

sub-01_T1map.json:

{


<<Parameter injected by the software/pipeline>>

"Sources":["bids:raw:sub-01/anat/sub-01_flip-1_VFA.nii.gz",
"bids:raw:sub-01/anat/sub-01_flip-2_VFA.nii.gz",
"bids:raw:sub-01/anat/sub-01_flip-3_VFA.nii.gz",
"bids:raw:sub-01/anat/sub-01_flip-4_VFA.nii.gz",
"bids:raw:sub-01/fmap/sub-01_TB1map.nii.gz"],
"EstimationPaper":"Deoni et. al.MRM, 2015",
"EstimationAlgorithm":"Linear",
"Units": "second",

<<Parameters that are constant across files in the (parent) file collection>>

"MagneticFieldStrength": "3",
"Manufacturer": "Siemens",
"ManufacturerModelName": "TrioTim",
"InstitutionName": "xxx",
"PulseSequenceType": "SPGR",
"PulseSequenceDetails": "Information beyond the sequence type that identifies
specific pulse sequence used (VB version, if not standard, Siemens WIP XXX
ersion ### sequence written by xx using a version compiled on mm/dd/yyyy/)",
"RepetitionTimeExcitation": "35",
"EchoTime": "2.86",
"SliceThickness": "5",

<<Relevant parameters that vary across the linking entity of the (parent) file collection>>

"FlipAngle": ["5","10","15","20"]

}

### Deriving the intended qMRI application from an ambiguous file collection

Certain file collection suffixes may refer to a generic data collection regime such as variable flip angle (VFA), rather than a more specific acquisition, for example, mag-
netization prepared two gradient echoes (MP2RAGE). Such generic acquisitions can serve as a basis to derive various qMRI applications by changes to the acquisition
sequence (for example, readout) type or by varying additional scan parameters.

If such an inheritance relationship is applicable between an already existing file collection and a new qMRI application to be included in the specification, the inheritor
qMRI method is listed in the table below instead of introducing a new file collection suffix. This approach aims at:


- preventing the list of available suffixes from over-proliferation,
- providing qMRI-focused BIDS applications with a set of meta-data driven rules to infer possible fitting options,
- keeping an inheritance track of the qMRI methods described within the specification.

File-collection suffix If REQUIRED metadata == Value OPTIONAL metadata ( **entity** / **fixed** ) Derived application name (NOT a
suffix)

VFA PulseSequenceType==SPGR DESPOT1
VFA PulseSequenceType==SSFP SpoilingRFPhaseIncrement(fixed) DESPOT2
MP2RAGE EchoTime(echo) MP2RAGE-ME
MPM EchoTime(echo) MPM-ME

In this table, (entity/fixed) denotes whether the OPTIONAL metadata that forms a new flavor of qMRI application for the respective suffix varies across files of a file
collection (which calls for using a linking entity) or fixed. If former is the case, the entity is to be added to the files in that file collection. Note that this addition MUST
be allowed by the priority levels given for that suffix in theentity table. If latter (fixed) is the case, filenames will remain the same; however, the optional metadata
(third column) may define the flavor of the application (fourth column) along with the conditional value of a required metadata field (second column).

A derived qMRI application becomes available if all the optional metadata fields listed for the respective file collection suffix are provided for the data. In addition,
conditional rules based on the value of a given required metadata field can be set for the description of a derived qMRI application. Note that the value of this required
metadata is fixed across constituent images of a file collection and defined in Method-specific priority levels for qMRI file collections.

For example, if the optional metadata field ofPulseSequenceTypeis SPGR for a collection of anatomical images listed by theVFAsuffix, the data qualifies forDESPOT1
T1 fitting. For the same suffix, if thePulseSequenceTypemetadata field has the value ofSSFP, and theSpoilingRFPhaseIncrementis provided as a metadata field, then
the dataset becomes eligible forDESPOT2T2 fitting application.

Please note that optional metadata fields listed in the deriving the intended qMRI application from an ambiguous file collection table are included in the optional (third)
column of the priority levels table for the consistency of this appendix.

### Introducing a new qMRI file collection

If a qMRI application cannot be interpreted as a subtype of an already existing suffix of a qMRI-related file collection, we RECOMMEND adhering to the following
principles to introduce a new suffix:

- All qMRI-relevant file collection suffixes are capitalized.
- Unless the pulse sequence is exclusively associated with a specific qMRI application (for example,MP2RAGE), sequence names are not used as suffixes.
- File collection suffixes for qMRI applications attain a clear description of the qMRI method that they relate to in the file collections appendix.
- Hyperlinks to example applications and reference method articles are encouraged whenever possible.
- If it is possible to derive a qMRI application from an already existing file collection suffix by defining a set of logical conditions over the metadata fields, the tables
    of the deriving the intended qMRI application from an ambiguous file collection and the anatomy data priority levels sections are extended instead of introducing
    a new suffix.


### Application-specific notes for qMRI file collections

#### Anatomy imaging data

General notes:

- Some BIDS metadata field values are calculated based on the values of other metadata fields that are not listed as required fields. These fields include:NumberShots.
    The calculation of the values may depend on the type of the acquisition. These acquisitions include:MP2RAGEandTB1SRGE.

**MP2RAGE** specific notes

**UNIT1** images Although theUNIT1image is provided as an output by the acquisition sequence, it is used as an input to offline calculation of aT1mapusing a dictionary
lookup approach. However,complexdata is needed for an accurate calculation of theUNIT1image, which is not commonly provided by the stock sequence. Instead, the
magnitudeandphaseimages are exported. Please see the relevant discussion atqMRLab issue #255.

Therefore, theUNIT1image provided by the scanner is RECOMMENDED to be stored under theanatraw dataset directory along with theMP2RAGEfile collection and to
be used as the primary input for quantifying aT1map.

If an additionalUNIT1image is calculated offline, then the output is to be stored in thederivativesdirectory with necessary provenance information.

**NumberShots** metadata field Note that the type ofNumberShotsfield can be either anumberor anarray of numbers.

- If a singlenumberis provided, this should correspond to the number ofSlicesPerSlaborReconMatrixPE. However, in this case,SlicePartialFourieror
    PartialFourierPEfraction is needed to calculate the number of partitionsbeforeandafterof the k-space center to calculate a T1 map.
- Ifbefore/aftercalculation is performed during the BIDS conversion of theMP2RAGEdata, then the value ofNumberShotsmetadata field can be given as a 1X2
    array, with first entry corresponding tobeforeand the second to theafter.

Formula:

If NumberShots is an array of numbers such that"NumberShots": [before, after], the values ofbeforeandafterare calculated as follows:

before = SlicesPerSlab*(SlicePartialFourier - 0.5)
after = SlicesPerSlab/2

See thisreference implementation.

Other metadata fields The value of theRepetitionTimeExcitationfield is not commonly found in the DICOM files. When accessible, the value ofEchoSpacing
corresponds to this metadata. When not accessible,2 X EchoTimecan be used as a surrogate.

Further information about otherMP2RAGEqMRI protocol fields can be found in theqMRLab documentation.

**TB1SRGE** specific notes

Calculation ofbeforeandafterentries forNumberShotsmetadata field ofTB1SRGEis more involved than that ofMP2RAGE. The formula can be found in areference
implementation, which requires information aboutBaseResolution(that is, image matrix size in PE direction), partial Fourier fraction in the PE direction, number of


reference lines for parallel imaging acceleration, and the parallel imaging acceleration factor in PE direction.

#### Radiofrequency (RF) field mapping

Some RF file collections call for the use of special notations that cannot be resolved by by entities that can generalize to other applications. Instead of introducing an
entity that is exclusive to a single application, method developers who commonly use these file collections for theMPMapplication reached the consensus on the use ofacq
entity to distinguish individual files. These suffixes include:TB1AFI,TB1TFL,TB1RFM, andRB1COR.

**TB1EPI** specific notes

Theflipandechoentities MUST be used to distinguish images with this suffix. The use offlipfollows the default convention. However, this suffix defines a specific use
case for theechoentity:

```
echo-1 echo-2
LowerEchoTime HigherEchoTime
Spin Echo (SE) image Stimulated Echo (STE) image
```
At eachFlipAngle, theTB1EPIsuffix lists two images acquired at two echo times. The first echo is a spin echo (SE) formed by the pulses alpha-2alpha. However, the
second echo in this method is generated in a different fashion compared to a typical MESE acquisition. The second echo is a stimulated echo (STE) that is formed by an
additional alpha pulse (that is, alpha-2alpha-alpha).

TheFlipAnglevalue corresponds to the nominal flip angle value of the STE pulse. The nominal FA value of the SE pulse is twice this value.

Note that the following metadata fields MUST be defined in the accompanying JSON files:

Field name Definition

TotalReadoutTime The effective readout length defined asEffectiveEchoSpacing * PEReconMatrix,
withEffectiveEchoSpacing = TrueEchoSpacing / PEacceleration
MixingTime Time interval between the SE and STE pulses

To properly identify constituents of this particular method, values of theechoentity MUST index the images as follows:

```
sub-01/
fmap/
sub-01_echo-1_flip-1_TB1EPI.nii.gz # SE
sub-01_echo-1_flip-1_TB1EPI.json
sub-01_echo-2_flip-1_TB1EPI.nii.gz # STE
sub-01_echo-2_flip-1_TB1EPI.json
sub-01_echo-1_flip-2_TB1EPI.nii.gz # SE
```

```
sub-01_echo-1_flip_2_TB1EPI.json
sub-01_echo-2_flip-2_TB1EPI.nii.gz # STE
sub-01_echo-2_flip-2_TB1EPI.json
```
**TB1AFI** specific notes

This method calculates a B1+ map from two images acquired at two interleaved excitation repetition times (TR). Note that there is no entity for the TR that can be used
to label the files corresponding to the two repetition times and the definition of repetition time depends on the modality (functionaloranatomical) in the specification.

Therefore, to properly identify constituents of this particular method, values of theacqentity SHOULD begin with eithertr1(lower TR) ortr2(higher TR) and MAY be
followed by freeform entries:

```
First TR Second TR Use case
_acq-tr1 _acq-tr2 Single acquisition
_acq-tr1Test _acq-tr2Test AcquisitionTest
_acq-tr1Retest _acq-tr2Retest AcquisitionRetest
```
```
sub-01/
fmap/
sub-01_acq-tr1_TB1AFI.nii.gz
sub-01_acq-tr1_TB1AFI.json
sub-01_acq-tr2_TB1AFI.nii.gz
sub-01_acq-tr2_TB1AFI.json
```
**TB1TFL** and **TB1RFM** specific notes

These suffixes describe two outputs generated by Siemenstfl_b1_mapandrf_mapproduct sequences, respectively. Both sequences output two images. The first image
appears like an anatomical image and the second output is a scaled flip angle map.

To properly identify files of this particular file collection, values of theacqentity SHOULD begin with eitheranatorfampand MAY be followed by freeform entries:

```
Anatomical (like) image Scaled flip angle map Use case
_acq-anat _acq-famp Single acquisition
_acq-anatTest _acq-fampTest AcquisitionTest
_acq-anatRetest _acq-fampRetest AcquisitionRetest
```
```
sub-01/
fmap/
sub-01_acq-anat_TB1TFL.nii.gz
sub-01_acq-anat_TB1TFL.json
```

```
sub-01_acq-famp_TB1TFL.nii.gz
sub-01_acq-famp_TB1TFL.json
```
The example above applies to theTB1RFMsuffix as well.

**RB1COR** specific notes

Thismethodgeneratesasensitivitymapbycombiningtwolowresolutionimagescollectedbytwotransmitcoils(thebodyandtheheadcoil)uponsubsequentscanswith
identical acquisition parameters.

To properly identify constituents of this particular method, values of theacqentity SHOULD begin with eitherbodyorheadand MAY be followed by freeform entries:

```
Body coil Head coil Use case
_acq-body _acq-head Single acquisition
_acq-bodyMTw _acq-headMTw MTwforMPM
_acq-bodyPDw _acq-headPDw PDwforMPM
_acq-bodyT1w _acq-headT1w T1wforMPM
```
```
sub-01/
fmap/
sub-01_acq-body_RB1COR.nii.gz # Body coil
sub-01_acq-body_RB1COR.json
sub-01_acq-head_RB1COR.nii.gz # Head coil
sub-01_acq-head_RB1COR.json
```

# Arterial Spin Labeling

These sections provide additional clarification for some specific topics within the BIDS specification for Arterial Spin Labeling.

## Which image is control and which is label?

Thecontrolandlabelimages are acquired with identical acquisition parameters, except that the blood magnetization flowing into the imaging region is effectively
inverted in thelabelimage compared to thecontrolimage. In case of doubt, an easy rule of thumb is that thedeltaM=control-labelsubtraction should result in a
perfusion-weighted image with a positive sign. For example, in the case of FAIR this would be selective inversion (control) and non-selective inversion (label).

## *_aslcontext.tsv : three possible cases

The*_aslcontext.tsvtable consists of a single column of labels identifying thevolume_typeof each volume in the corresponding*_asl.nii[.gz]file. See below
examples of the three*_aslcontext.tsvcases, in order of decreasing preference.

#### Case 1: *_asl.nii[.gz] consists of volume_types control , label

In most cases, the ASL timeseries provided by the scanner consist of a series ofcontrolandlabel, and optionallym0scanvolumes. In this case, only thecontrol,label,
and optionallym0scanvolumes should be stored in the*_asl.nii[.gz], and the exact volume_type series should be specified in the*_aslcontext.tsv.

Example of*_aslcontext.tsv:

volume_type
control
label
control
label
m0scan


#### Case 2: *_asl.nii[.gz] consists of volume_types deltam (scanner does not export control or label volumes)

In some cases,controlandlabelvolumes are lacking within the acquired ASL timeseries, but the intermediatedeltam- and optionally anm0scan- volume is recon-
structed/exported by the scanner. In this case, thedeltamshould be included in the*_asl.nii[.gz]and specified in the*_aslcontext.tsv.

Example of*_aslcontext.tsv:

volume_type
deltam
m0scan

#### Case 3: *_asl.nii[.gz] consists of volume_type cbf (scanner does not export control , label , or deltaM volumes)

Ifcontrolandlabelor intermediate ASL volumes are not reconstructed or exported, but a pre-calculatedcbf- and optionally am0scan- volume is provided by the
scanner, thecbfshould be included in the*_asl.nii[.gz]and specified in the*_aslcontext.tsv.

Example of*_aslcontext.tsv:

volume_type
cbf
m0scan

### Summary Image of the most common ASL sequences

The following images illustrate the main BIDS metadata fields for threeArterialSpinLabelingType’s:CASL,PCASL, andPASL. Images are courtesy of, and adapted with
permission from Y. Suzuki andOSIPI Task force 4.1: ASL lexicon milestone 1.


#### (P)CASL sequence

For(P)CASL,specifyingtheLabelingDurationandthePostLabelingDelayisrequired. TheLabelingDurationisdefinedasthetotaldurationofthelabelingpulsetrain
inseconds.PostLabelingDelayisthetimeinsecondsaftertheendofthelabelinguntilthemiddleoftheexcitationpulseappliedtotheimagingslab(for3Dacquisition)or
first slice (for 2D acquisition). Additionally, theBackgroundSuppressionPulseTime’s is required in caseBackgroundSuppressionwas applied. This an array of numbers
containing the timing in seconds of the background suppression pulses with respect to the start of the labeling. In the case ofPCASL, the recommendedPCASLTypefield
defines the type of the gradient pulses used in thecontrolcondition (balancedorunbalanced), whereas in case ofCASL,the recommendedCASLTypefield describes if a
separate coil is used for labeling (single-coilordouble-coil).


#### (P)CASL Labeling Pulses


SeveralrecommendedmetadatafieldsdescribethelabelingpulsesofthelabelingpulsetraininPCASL.TheLabelingPulseAverageGradientandtheLabelingPulseMaximumGradient
are the average labeling gradient and the maximum amplitude of the gradient switched on during the application of the labeling RF pulse(s), in milliteslas per meter.
TheLabelingPulseAverageB1is the average B1-field strength of the RF labeling pulses in microteslas. TheLabelingPulseDurationandLabelingPulseIntervalare
the duration of, and the delay between the peaks of the individual labeling pulses in milliseconds.

#### PASL sequence

For PASL, specifying thePostLabelingDelayis required. PostLabelingDelayis the time, in seconds, from the middle of the labeling pulse until the middle of the
excitation pulse applied to the imaging slab (for 3D acquisition) or first slice (for 2D acquisition). Additionally, theBolusCutOffFlagfield is required, which is a boolean
indicating if a bolus cut-off technique has been applied.


WhenBolusCutOffFlagis set true forPASL, two additional metadata fields are required: BolusCutOffTechniqueandBolusCutOffDelay. In this example, the
BolusCutOffTechnique, which is the name of the technique used for applying a bolus cut-off, is QUIPSS-II consisting of only one bolus cut-off pulse. The
BolusCutOffDelayis therefore a number, representing the duration between the end of the labeling and the start of the bolus cut-off saturation pulse, in seconds.


In this example, theBolusCutOffTechniqueapplied is Q2TIPS, consisting of multiple bolus cut-off pulses. In this case, only the duration of the first and last pulse should
be specified inBolusCutOffDelay.

### Flowchart (based on dependency table)

The specification includes a dependency table, describing metadata field dependencies for ASL. This flowchart is intended to further clarify that table.



# Cross modality correspondence

## PET-MRI correspondence

```
When sharing MRI data alongside with PET data, please pay specific attention to the format the MR images are in. It is important to note whether the MR images have
been unwarped in order to correct for gradient non-linearities, indicated by theNonlinearGradientCorrectionmetadata field (see Magnetic Resonance Imaging Data
```
- Sequence Specifics). The reason for this is that the MRI needs to be corrected for nonlinear gradients in order to fit the accompanying PET scans for co-registration
    (Knudsen et al. 2020,doi:10.1177/0271678X20905433; Norgaard et al. 2019,doi:10.1016/j.neuroimage.2019.05.055).


# Changelog

## v1.8.0(2022-10-29)

- [FIX] Drop the functional and f for NIRS#1325(rob-luke)
- [FIX][SCHEMA] Add conditionals for PET ReconMethod* and ReconFilter#1299(bendhouseart)
- [ENH] use schema to mention which ”top directories” are allowed#1289(Remi-Gau)
- [ENH] Add glossary links to all tables#1268(tsalo)
- [ENH] Remove redundant entity definitions on MRI page#1265(tsalo)
- [ENH] Standardize and organize entity descriptions#1264(tsalo)
- [ENH] Add filename template legend#1259(Remi-Gau)
- [MISC] Reorder appendices#1256(tsalo)
- [MISC] Clarify: FieldMap PE technique --> no SPM#1253(CPernet)
- [MISC] Adding qMRI BIDS article reference (BEP001)#1251(agahkarakuzu)
- [ENH] Link to filename element definitions in filename templates#1228(tsalo)
- [MISC] Remove label format and inheritance principle redundancies in fMRI section#1197(Remi-Gau)
- [ENH] add task metadata to PET#1196(Remi-Gau)
- [FIX] clarify which file to list in scans.tsv for file formats with multiple files#1178(sappelhoff)
- [FIX] add recommendation to fully omit non-compulsory data that is n/a#1171(sappelhoff)
- [FIX] Discourage use of ”sample” in events if sampling frequency is ambiguous, add guidelines for precision#1140(sappelhoff)
- [FIX] Clarify MEG empty-room recommendations#1125(robertoostenveld)
- [FIX] clarify no blank and duplicated headers in TSV#1116(sappelhoff)
- [ENH] Added the specification for using HED libraries in BIDS#1106(VisLab)
- [ENH] Microscopy: NGFF format support#1104(TheChymera)
- [ENH] Add Microscopy-BIDS citation#1102(mariehbourget)
- [FIX] MEG link typo#1100(xi)
- [FIX] IntendedFor in (i)EEG is dataset relative#1093(sappelhoff)
- [MISC] make dataset_description.Authors RECOMMENDED#1092(sappelhoff)
- [ENH] adding optional _rec-label to DWI#1090(dorahermes)
- [ENH] State of the schema sprint#1075(effigies)


- [MISC] Preface each macro call with comment#1052(Remi-Gau)
- [ENH] allow for .png and .tif in eeg/ieeg/meg as allowed for micr#1049(yarikoptic)
- [FIX] typo in ”rawdata” example#1045(sappelhoff)
- [MISC] consistently use ”directory” instead of ”folder” as a term#1044(sappelhoff)
- [MISC] Update CODEOWNERS#1040(erdalkaraca)
- [ENH] Allow README file extensions.#1033(mateuszpawlik)
- [MISC] Rewrite and update html build instructions#1032(sappelhoff)
- [FIX] Clarify that BIDS standard template data is to be in scanner coordinates (MEG, iEEG, EEG)#1031(alexrockhill)
- [FIX] Add coordsystem-specific definition of DigitizedHeadPoints#1023(tsalo)
- [FIX] PET Spec; added known DICOM tags, fixed tag error, updated citation, clarified scale factor.#1021(bendhouseart)
- [MISC] clarify copyright for logo#1019(sappelhoff)
- [FIX] Change recording entity to REQUIRED for pet/blood modality#1005(ghisvail)
- [ENH] Microscopy: Add IntendedFor metadata field to photo files#1000(mariehbourget)
- [ENH] Introduce the atlas entity for derivatives data#997(sebastientourbier)
- [ENH] Clearly define ”entity” in common principles#947(Lestropie)
- [ENH] Add BIDS URIs and deprecate relative paths, RawSources and (possibly unused) BasedOn#918(effigies)
- [ENH] BEP030: Functional Near-Infrared Spectroscopy#802(rob-luke)
- [FIX] Clarify run entity to accommodate multiple imaging modalities#760(yarikoptic)

### v1.7.0(2022-02-15)

- [FIX] Use wikipedia for TIFF URL, adobe’s page is 404ing now#1007(yarikoptic)
- [FIX] update highlighting of examples, JSON keys and values, and TSV headers or values in the schema#998(Remi-Gau)
- [MISC] minor wording and consistency improvements for channels.tsv in EEG, MEG, iEEG#993(sappelhoff)
- [FIX] typo: extra sentence in anat section#991(Remi-Gau)
- [FIX] Optionally support echo entity for VFA suffix#989(TheChymera)
- [FIX] update definition acq_time for sessions.tsv#986(Remi-Gau)
- [FIX] add microscopy to modalities in schema#984(Remi-Gau)
- [MISC] update steering group composition#976(Remi-Gau)
- [MISC] customize footer on html spec#975(sappelhoff)
- [FIX] Update HED appendix to comply with current HED version#970(VisLab)
- [ENH] Update B0Field metadata to accommodate single-blip fieldmaps#968(effigies)
- [FIX] Reword front page#958(arokem)
- [MISC] Update links to starter kit website#957(effigies)
- [FIX] Entity table: Clarify meaning of empty cells#955(Lestropie)
- [MISC] Add Eric Earl as a Maintainer#953(ericearl)
- [FIX] Spelling errors in appendices#951(Lestropie)
- [FIX] Broken hyperlink in entity list file#949(Lestropie)
- [FIX] Rewrite inheritance principle#946(Lestropie)
- [FIX] Typo: ECG_headshape#942(Moo-Marc)


- [FIX] description: dwi is specialized T2 weighting, not T2*#939(sappelhoff)
- [FIX] relax unrealistically strict requirements with ieeg channels.tsv ’name’ column#938(sappelhoff)
- [FIX] Add links from derivatives section to entity list#936(sappelhoff)
- [FIX] Remove repeated words#934(DimitriPapadopoulos)
- [FIX] Clarify that EDF/BDF files MUST have lower case extensions in BIDS#927(adam2392)
- [ENH] Generate glossary page from schema#923(tsalo)
- [ENH] Render valid value restrictions in tables based on object definitions in schema#921(tsalo)
- [ENH] addhemientity to schema#917(Remi-Gau)
- [ENH] update and reformat table for template in coordinate system page#903(Remi-Gau)
- [ENH] add details for content of\*\_beh.json#902(Remi-Gau)
- [FIX] small typo in json example#897(Remi-Gau)
- [INFRA] Document *.webm video files as binary#895(DimitriPapadopoulos)
- [SCHEMA] Reorganize schema code into a package#892(tsalo)
- [FIX] Clarify shifting dates RECOMMENDED, add example EDF#891(sappelhoff)
- [INFRA] fix draft rendering css on mobile or when browser window is narrow#889(sappelhoff)
- [MISC] Add an animated BIDS logo#886(adswa)
- [SCHEMA] Consolidate schema files by term type#883(tsalo)
- [ENH] BEP031: Microscopy#881(mariehbourget)
- [INFRA] jQuery 3.4.1 → 3.6.0#875(DimitriPapadopoulos)
- [INFRA] Add ”codespell” tool to CI checks to catch typos sooner#873(DimitriPapadopoulos)
- [INFRA] Several style fixes (Flake8) for Python code in the repo#872(DimitriPapadopoulos)
- [MISC] add Anthony as maintainer#868(Remi-Gau)
- [MISC] add ”forward slash” requirement for paths to common principles#867(sappelhoff)
- [ENH] Add ”ScanRAS” as an accepted coordinate frame for ieeg#866(alexrockhill)
- [INFRA] Add .lgtm.yml file for better usage of LGTM CI tool#865(DimitriPapadopoulos)
- [FIX] update physio bids name in longitudinal study page examples#863(Remi-Gau)
- [INFRA] Enforce consistent line endings via .gitattributes#861(DimitriPapadopoulos)
- [FIX] Clarify case collision intolerance as a file naming principle#858(yarikoptic)
- [INFRA] LGTM recommendation: Unused local variable#853(DimitriPapadopoulos)
- [INFRA] LGTM warning: Variable defined multiple times#851(DimitriPapadopoulos)
- [FIX] Typos found by codespell#848(DimitriPapadopoulos)
- [ENH] Add links to example datasets for each modality#845(Remi-Gau)
- [INFRA] Add basic documentation on how to use metadata table macros#840(Remi-Gau)
- [ENH] make ”Institutional department name” available for all datatypes#839(Remi-Gau)
- [INFRA] use macro to render examples in a ”tree” like fashion#837(Remi-Gau)
- [FIX] Add angio suffix to the non-parametric aMRI suffix table#835(tsalo)
- [FIX] Remove last hardcoded suffix table#833(tsalo)
- [MISC] make explicit that EDF+ (and for EEG: BDF+) are included in iEEG / EEG format requirements#831(sappelhoff)
- [SCHEMA] Add TSV column files#827(tsalo)
- [ENH] add metadata to PET calibration factor: ”DoseCalibrationFactor”#825(CPernet)


- [FIX] correct file location of scans.tsv file in example#824(ghisvail)
- [MISC] update available datatypes in specification#819(sappelhoff)
- [FIX] document required column order MEG, EEG, iEEG, PET, and fix typo iEEG#818(sappelhoff)
- [ENH] BEP031 - New columns to participants.tsv file#816(mariehbourget)
- [MISC] make table headers bold#815(Remi-Gau)
- [FIX] What is a composite instance? Change to measurement for non MRI modalities?#813(rob-luke)
- [ENH] BEP031 - New entity: sample and samples.tsv file#812(mariehbourget)
- [ENH] Add device and acquisition metadata for physio files#806(Remi-Gau)
- [MISC] Move section on sessions.tsv file: longitudinal files -> modality agnostic files#805(Remi-Gau)
- [ENH] Make explicit that ”task” metadata applies to ”beh” modality#804(Remi-Gau)
- [MISC] Make MRI-centric language more general in Events#801(sappelhoff)
- [ENH] clarify that entities MUST be unique#800(sappelhoff)
- [MISC] deprecate DCOffsetCorrection field from ieeg.json: Use SoftwareFilters field instead#799(sappelhoff)
- [FIX] Deprecate ScanDate (PET) in favor of AcquisitionTime in scans.tsv files#798(mnoergaard)
- [MISC] add IETF standard link for json#797(sappelhoff)
- [INFRA] In PDF, color every other row in table in light gray fill#794(sappelhoff)
- [MISC] add link to guide on how to write a good README#793(sappelhoff)
- [SCHEMA] Apply schema rules to entity values#792(tsalo)
- [INFRA] fix md ci and update ci badges#791(sappelhoff)
- [SCHEMA] Use macro for filename templates in file collections appendix#787(tsalo)
- [FIX] consistently refer to DICOM Tags throughout the specification#786(Hboni)
- [FIX] Amend note about *b*-vecs on DWI specs#782(oesteban)
- [INFRA] add CI to find trailing whitespace#780(sappelhoff)
- [MISC] Add info on HED key to common principles#777(sappelhoff)
- [ENH] add EEGLAB as valid coordinate system for EEG#775(sappelhoff)
- [SCHEMA] Add metadata term files#774(tsalo)
- [SCHEMA] Add suffix term files#772(tsalo)
- [ENH] Allow encoding the fieldmapping intent of the protocol#622(oesteban)
- [FIX] Correct iEEG example that contained double suffixes#463(yarikoptic)
- [ENH] introduce GeneratedBy to ”core” BIDS#440(yarikoptic)

### v1.6.0(2021-04-22)

- [FIX] Typos discovered by codespell#784(yarikoptic)
- [FIX] Rename ”Unit” metadata to ”Units” for consistency with existing fields#773(effigies)
- [FIX] typo in pet: institution -> institutional#771(sappelhoff)
- [INFRA] install git in linkchecker job#767(sappelhoff)
- [INFRA] Fix CircleCI workflows#764(sappelhoff)
- [INFRA] do not run remark on auto CHANGES#755(sappelhoff)
- [FIX] Mix up (typo) between ficiduals and landmarks in EEG spec#754(rob-luke)


- [INFRA] updating remark, CIs, contributor docs#745(sappelhoff)
- [FIX] schema for i/eeg coordsys+elecs: sub-ses-acq-space are allowed entities#743(sappelhoff)
- [MISC] move schema documentation into the schema directory#740(Remi-Gau)
- [MISC] standardize string examples format in tables#739(Remi-Gau)
- [MISC] Clarify participant_id in participants.tsv file if it exists#738(adam2392)
- [FIX] split MEG files should be listed separately in scans.tsv#735(eort)
- [FIX] 1) Clarify appropriate labels for space entity, 2) Clarify channels+electrodes do not have to match#734(sappelhoff)
- [MISC] refactor stimuli mentioning sections in the events page#697(Remi-Gau)
- [ENH] Bep 009: Positron Emission Tomography#633(melanieganz)

### v1.5.0(2021-02-23)

- [MISC] Updated TotalAcquiredVolumes into TotalAcquiredPairs#742(effigies)
- [SCHEMA] Update qMRI fieldmap schema#728(effigies)
- [FIX] Add deprecated anatomical MRI suffixes back into schema#725(tsalo)
- [FIX] Correct schema irregularities for func datatype#724(tsalo)
- [FIX] Make flip optional for MP2RAGE#722(tsalo)
- [FIX] Correct entity names in YAML files#720(tsalo)
- [ENH] Clarify run indexing information for MRI acquisitions#719(effigies)
- [ENH] Harmonize CoordinateSystem details for MRI, MEG, EEG, iEEG#717(sappelhoff)
- [SCHEMA] Update entity YAML keys#714(effigies)
- [MISC] Added full names for some contributors in .mailmap file#705(yarikoptic)
- [INFRA] Migrate md and yml checks from travis to GH actions#693(sappelhoff)
- [INFRA] Move part entity to before recording entity#692(tsalo)
- [ENH] BEP001 - qMRI maps and some additional metadata#690(agahkarakuzu)
- [ENH] BEP001 - Entity-linked file collections#688(effigies)
- [ENH] BEP001 - New entities: inv & mt#681(agahkarakuzu)
- [MISC] add contributing guidelines to add figures in the specs#679(Remi-Gau)
- [MISC] use RFC 2119 language in legend of the ”volume timing” table#678(Remi-Gau)
- [FIX] Add OPTIONAL acq entity to channels.tsv, events.tsv to match electrophysiological acquisitions#677(sappelhoff)
- [MISC] Update all links to use HTTPS whenever possible.#676(gllmflndn)
- [INFRA] Relax line length limit for linting YAML files#673(effigies)
- [ENH] BEP001 - New entity: flip#672(agahkarakuzu)
- [ENH] BEP001 - RepetitionTimeExcitation and RepetitionTimePreparation#671(agahkarakuzu)
- [ENH] Bep 005: Arterial Spin Labeling#669(sappelhoff)
- [FIX] Added white space after table#660(robertoostenveld)
- [MISC] add remi as maintainer#657(Remi-Gau)
- [MISC] update Contributing with info on how to respond to reviews#655(Remi-Gau)
- [FIX] add paragraph on MEG specific ”markers” suffix in MEG spec#653(sappelhoff)
- [FIX] Rewrite the MRI/fieldmaps subsection for consistency with the rest of specs#651(oesteban)


- [FIX] Fixing template string on electrodes for eeg and ieeg.#650(adam2392)
- [ENH] Update genetics-BIDS citation#646(effigies)
- [SCHEMA] Add derivatives entities to the schema#645(tsalo)
- [MISC] add brief note that TSV example in the spec may currently use either tab or space characters#643(yarikoptic)
- [ENH] Add ”multipart DWI” acquisitions and refactor DWI specifications#624(oesteban)
- [SCHEMA] Render schema elements in text#610(tsalo)
- [ENH] Add part entity for complex-valued data#424(tsalo)

### v1.4.1(2020-10-13)

- [INFRA] minor robustness enhancements to pdf build shell script#642(yarikoptic)
- [FIX] consistent CoordinateSystem fields for ephys#641(sappelhoff)
- [INFRA] set up github action to detect latin phrases#636(Remi-Gau)
- [ENH] Add a definition for ”deprecation”#634(sappelhoff)
- [MISC] consolidate BIDS citations in introduction#630(sappelhoff)
- [FIX] URI ”definition” and recommendation#629(Remi-Gau)
- [FIX] change remaining latin expressions (etc and i.e.)#628(Remi-Gau)
- [FIX] replace ”e.g.,” by ”for example”#626(Remi-Gau)
- [FIX] arrays of 3D coordinates MUST supply numeric values in x, y, z order#623(sappelhoff)
- [FIX] Accidentally swapped Neuromag/Elekta/MEGIN cross-talk & fine-calibration filename extensions#621(hoechenberger)
- [FIX] improve HED documentation#619(VisLab)
- [INFRA] Move MRI section headings up a level#618(tsalo)
- [INFRA] SCHEMA: Declare entities by concept names, add entity field for filename components#616(effigies)
- [FIX] Change wrong text references from *CoordinateSystemUnits to *CoordinateUnits#614(sappelhoff)
- [ENH] Describe arbitrary units in Common Principles#606(tsalo)
- [FIX] Clarify data types and requirement levels for all JSON files#605(sappelhoff)
- [INFRA] downgrade github-changelog-generator to 1.14.3 due to issue with 1.15.2#600(sappelhoff)
- [FIX] tighter rules for sharing MEG cross-talk and fine-calibration .fif files#598(sappelhoff)
- [MISC] Add tsalo as a BIDS maintainer#597(tsalo)
- [FIX] clarify definition of events in common principles#595(sappelhoff)
- [INFRA] use --release-branch option in github-changelog-generator#594(sappelhoff)
- [ENH] Define ”modality” and clarify ”data type”#592(effigies)
- [FIX] Adjust index definition to be nonnegative integer#590(nicholst)
- [MISC] fix links, make json object links consistent, fix pandoc rendering#587(sappelhoff)
- [FIX] Fix link in Common principles#583(tsalo)
- [ENH] Specify how to share cross-talk and fine-calibration for Neuromag/Elekta/MEGIN data#581(sappelhoff)
- [ENH] Specify echo and run indices are nonnegative integers in schema#578(tsalo)
- [ENH] add optional presentation software name, version, OS, and code to events.json#573(Remi-Gau)
- [ENH] added PPG as an accepted channel type for EEG, MEG and iEEG#570(robertoostenveld)
- [INFRA] Move entity definitions to a separate page#568(tsalo)


- [INFRA] enable pandoc emojis for the pdf build#562(sappelhoff)
- [INFRA] Auto adjust table fences before PDF conversion#560(sebastientourbier)
- [ENH] Support run and acq entities in behavior-only data#556(tsalo)
- [FIX] Clarify requirement levels for TSV metadata fields#555(sappelhoff)
- [FIX] Reorganize rec, ce entities, _defacemask#550(emdupre)
- [FIX] Clarify Upper-casing of Channels.tsv Channel Type#548(adam2392)
- [ENH] Extend date time information to include optional UTC syntax, warn about FIF requirements#546(sappelhoff)
- [FIX] clarify that <physio|stim>.json is REQUIRED#542(sappelhoff)
- [FIX] Replace all non-breaking spaces with vanilla spaces#536(nicholst)
- [FIX] Clarify indices are nonnegative integers.#535(nicholst)
- [FIX] Clarify use of session entity in filenames#532(Moo-Marc)
- [ENH] Add the ability of users to specify an explicit HED.xml schema for validation.#527(VisLab)
- [FIX] clarify that scans.json is allowed and recommended#523(sappelhoff)
- [INFRA] add copyright holder to license.#521(sappelhoff)
- [FIX] clarify XXXCoord* in the coordinate systems appendix#520(sappelhoff)
- [ENH] Updatebeh/specification to contrast with any neural recordings#515(effigies)
- [FIX] restructure and clarify *_physio/*_stim section#513(sappelhoff)
- [FIX] clarify file formats in EEG, iEEG#511(sappelhoff)
- [FIX] Add links and release dates to pre GH changelog, fix formatting#509(sappelhoff)
- [FIX] Clarify thatacq\_timeinscans.jsonrefers to first data point acquired#506(tsalo)
- [INFRA] make circle artifact link a GH action, point to pdf#505(sappelhoff)
- [FIX] Typos in DECISION-MAKING file#504(tsalo)
- [ENH] AddCommenting on a PRto CONTRIBUTING.md#490(franklin-feingold)
- [FIX] clarify MEG empty-room recording naming conventions#480(sappelhoff)
- [INFRA] Convert entity table to yaml#475(tsalo)
- [FIX] Recommend SI units formatting to adhere to CMIXF-12#411(sappelhoff)

### v1.4.0(2020-06-11)

- [FIX] Clarify language on unsetting a key/value pair#495(nicholst)
- [ENH] optionally allow LICENSE file#483(sappelhoff)
- [INFRA] linkchecker - ignore github pull and tree URLs#477(yarikoptic)
- [ENH] Allow fractional seconds in scans file datetimes#470(tsalo)
- [MISC] Maintainers -Scoperesponsibility#467(franklin-feingold)
- [FIX] Align tables in MRI section#465(sappelhoff)
- [FIX] Drop\_part-reference from example, introduce\_split-entity#460(sappelhoff)
- [FIX] clarify participants tsv+json with examples and recommendations#459(sappelhoff)
- [FIX] Remove BESA from list of restricted keywords of EEG coordsystems#457(sappelhoff)
- [INFRA] add steps for release protocol (PDF upload)#455(sappelhoff)
- [FIX] Add reference to PDF on front page of specification#452(nicholst)


- [INFRA] Add conditional for link-checking releases#451(franklin-feingold)
- [FIX] unordered list formatting in BEP018#449(sappelhoff)
- [FIX] fix inconsistencies for task label between sections#446(Remi-Gau)
- [FIX] update DECISION-MAKING.md document with new governance#441(sappelhoff)
- [ENH] BEP 003: Common Derivatives#265(effigies)
- [ENH] Add Glossary of terms/abbreviations used in the specification#152(yarikoptic)

### v1.3.0(2020-04-14)

- [INFRA] add zenodo badge to README#447(sappelhoff)
- [MISC] Added contributors from VisLab#444(VisLab)
- [FIX] Clarify snake_case+CamelCase in TSV+JSON#442(sappelhoff)
- [FIX] Eliminate web/online-specific language#437(nicholst)
- [INFRA] ensure build_docs_pdf CircleCI job runs last#436(sappelhoff)
- [INFRA] Add issue templates for GitHub#434(sappelhoff)
- [INFRA] Get latest PDF build from CircleCI artifacts#433(sappelhoff)
- [INFRA] Update release protocol#432(franklin-feingold)
- [INFRA] add support for building PDF versions of the spec#431(Arshitha)
- [ENH] Explicitly mention bids-validator and update link#428(sappelhoff)
- [INFRA] use new bids-maintenance GitHub account to take over automatic work#426(sappelhoff)
- [FIX] Unify section titles and table-of-contents entries#422(nicholst)
- [INFRA] add # before heading in CHANGES#419(sappelhoff)
- [INFRA] fix heading of auto changelog to be a markdown header#417(sappelhoff)
- [ENH] Add OPTIONAL EthicsApprovals field to dataset description#412(effigies)
- [ENH] BEP 018 - Genetic Information#395(effigies)

### v1.2.2(2020-02-12)

- [FIX] improve wording on data dictionaries#410(sappelhoff)
- [MISC] update contributions by CPernet#409(CPernet)
- [MISC] Add Sébastien Tourbier to contributors#394(sebastientourbier)
- [FIX] consistent units description between EEG/MEG/iEEG. Clarify (derived) SI units + prefixes#391(sappelhoff)
- [MISC] moved list of extension proposals to the main BIDS website#389(robertoostenveld)
- [FIX] Typos and clarifications#386(apjanke)
- [INFRA] Add watermark to drafts#383(effigies)
- [MISC] Teon Brooks retiring moderator duties for BEP021#381(teonbrooks)
- [FIX] clarify that string is expected for HowToAcknowledge field in dataset_description.json#380(sappelhoff)
- [MISC] Typo and style#378(TheChymera)
- [FIX] divide readme into 3 parts#374(sappelhoff)


- [FIX] Refer to BIDS consistently, instead of ”<Modality>-BIDS”#366(sappelhoff)
- [FIX] Change recommended anonymization date from 1900 to 1925#363(alexrockhill)
- [FIX] Minor fixups of inconsistencies while going through a PDF version#362(yarikoptic)
- [FIX] clarify that filters should be specified as object of objects#348(sappelhoff)
- [FIX] Clarify channels.tsv is RECOMMENDED consistently across ephys#347(sappelhoff)
- [FIX] Typo fix (contract -> contrast) in events documentation#346(snastase)
- [MISC] rm TOC.md - seems no longer pertinent/used#341(yarikoptic)
- [MISC] Move the PR template to a separate directory and improve contents#338(jhlegarreta)
- [INFRA] Find npm requirements file in Circle#336(franklin-feingold)
- [ENH] Clarify phenotypic and assessment data in new section#331(sappelhoff)
- [MISC] add information about continuous integration checks to PR template#330(sappelhoff)
- [FIX] FixCommon principles Key/value filessection level#328(jhlegarreta)
- [INFRA] Set the maximum heading length lint check tofalse#325(jhlegarreta)
- [FIX] Number explicitly all cases in MRI field map section headers#323(jhlegarreta)
- [FIX] Add SoftwareFilters to EEG sidecar example#322(Remi-Gau)
- [MISC] Fixing Travis errors with Remark#320(franklin-feingold)
- [INFRA] Link to doc builds in CI checks#315(jasmainak)
- [MISC] Add BEP027 - BIDS Execution to BEP list#314(effigies)
- [FIX] Add CBV and phase to Entity table#312(tsalo)
- [FIX] Normalization of template-generated standard spaces#306(oesteban)
- [ENH] Release protocol notes#304(franklin-feingold)
- [INFRA] Adding contributor appendix sentence to PR template#299(franklin-feingold)
- [ENH] Added discontinuous datatype for EEG and iEEG#286(wouterpotters)
- [FIX] Clarify paragraph about custom data types#264(effigies)

### v1.2.1(2019-08-14)

- [FIX] repair link in anatomical MRI table#297(sappelhoff)
- [ENH] Clarify requirements in Release Protocol#294(franklin-feingold)
- [INFRA] Use linkchecker (from a dedicated docker image) to check all URLs#293(yarikoptic)
- [ENH] Adding Contributors and updating contributions#284(franklin-feingold)
- [MISC] update Code of Conduct contact#281(franklin-feingold)
- [ENH] Update contributing guide and README to make discussion forums easy to find#279(emdupre)
- [ENH] Starter Kit dropdown menu#278(franklin-feingold)
- [ENH] BEP Update#277(franklin-feingold)
- [INFRA] Update pipenv#274(sappelhoff)
- [INFRA] Transpose the entity table and link to text anchors describing each entity#272(sappelhoff)
- [ENH] Add Twitter badge to README and link to website to landing page#268(franklin-feingold)
- [ENH] adding release guidelines#267(franklin-feingold)
- [FIX] Common principles: Fix filename in inheritance principle#261(Lestropie)


- [MISC] update modality references#258(sappelhoff)
- [INFRA] adding logo to RTD#256(franklin-feingold)
- [INFRA] add footer, replacing mkdocs/material advert with Github link#250(sappelhoff)
- [MISC] rename logo files, add a README of where they come from, fix favicon#249(sappelhoff)
- [MISC] updating MEG doc links, manufacturer names, and adding a missing MEG example#248(sappelhoff)
- [ENH] Add favicon to RTD#246(franklin-feingold)
- [MISC] Update Authors in BEP025#241(josator2)
- [MISC] Document BEPs that are not active anymore, but have not been merged#240(sappelhoff)
- [FIX] remove ManufacturersAmplifierModelName (again)#236(robertoostenveld)
- [INFRA] Update release protocol#235(effigies)
- [INFRA] Enable version panel for quickly finding previous versions#232(effigies)
- [FIX] Clarify Appendix II: The list of licenses only lists examples#222(sappelhoff)
- [FIX] Trivial column header fix#220(nicholst)
- [INFRA] Add clarification on merge methods to DECISION_MAKING#217(sappelhoff)
- [INFRA] Enable permalink urls to appear at (sub)section headings#214(yarikoptic)
- [INFRA] bump up mkdocs-materials version#211(sappelhoff)
- [MISC] Fix github username for @chrisgorgo#204(chrisgorgo)
- [FIX] clarify example 3 in common principles (inheritance)#202(sappelhoff)
- [MISC] Expand entity table for MEG/EEG/iEEG specific files#198(sappelhoff)
- [FIX] make iEEG ToC more consistent with MEG and EEG#191(robertoostenveld)
- [FIX] Clarify use of acq and task parameters in EEG, MEG, and iEEG#188(sappelhoff)
- [FIX] clarify use of tools for CTF data renaming#187(sappelhoff)
- [MISC] Add bep006 and bep010 to completed beps and fix links#186(sappelhoff)
- [FIX] change file for definition of electrical stimulation labels from _electrodes.json to _events.json#185(ezemikulan)
- [ENH] relax ieeg channel name requirements of letters and numbers only#182(sappelhoff)
- [FIX] make MEG section headings and ToC consistent to the EEG and iEEG specs#181(robertoostenveld)
- [FIX] make section headings and ToC consistent between meg and eeg specs#180(robertoostenveld)
- [MISC] Spelling fixes#179(DimitriPapadopoulos)
- [ENH] Alternative directory organization for raw, derived, and source data#178(chrisgorgo)
- [INFRA] Adding instructions for naming PRs#177(chrisgorgo)
- [MISC] Introducing Stefan Appelhoff as the first Maintainer#176(chrisgorgo)
- [FIX] Clarify name of ”BrainVision” format#175(JegouA)
- [FIX] Fixes spelling of continuous#171(emdupre)
- [FIX] Clarify continuous recording metadata fields#167(effigies)
- [FIX] changed reference ofdcm2niitodcm2niix#166(DimitriPapadopoulos)
- [FIX] Removing a leftover file#162(chrisgorgo)
- [FIX] Specify marker filenames for KIT data (MEG)#62(monkeyman192)
- [FIX] Remove father-level for meg filetypes other than BTi/4D data#19(teonbrooks)


### v1.2.0(2019-03-04)

- [MISC] Adding Dimitri Papadopoulos Orfanos to the list of contributors#157(DimitriPapadopoulos)
- [FIX] use ”specification” not ”protocol” to refer to BIDS#156(yarikoptic)
- [FIX] Fix example misalignment#155(DimitriPapadopoulos)
- [INFRA] Update Pipfile.lock#144(franklin-feingold)
- [ENH] clarify decimal sep and numerical notation convention#143(sappelhoff)
- [ENH] clarify encoding of README, CHANGES, TSV, and JSON files#140(sappelhoff)
- [MISC] Update site_name and release protocol#137(franklin-feingold)
- [FIX] Example for IntendedFor was missing session indicator in the filename#129(yarikoptic)
- [ENH] Add ”_phase” suffix to func datatype for functional phase data#128(tsalo)
- [MISC] Update to Release_Protocol.md#126(franklin-feingold)
- [MISC] Update tag naming convention#123(chrisgorgo)
- [ENH] Merge bep006 and bep010#108(sappelhoff)
- [MISC] Adding formal decision-making rules#104(chrisgorgo)
- [FIX] number of small corrections to the specification#98(robertoostenveld)

### v1.1.2(2019-01-10)

- [ENH] Global fields in data dictionaries#117(chrisgorgo)
- [MISC] Propose BEP026 MER#116(greydongilmore)
- [FIX] Remove duplicate entries in MEG table#113(franklin-feingold)
- [MISC] Propose BEP025 MIDS#110(josator2)
- [FIX] repair links#106(sappelhoff)
- [INFRA] Autogenerate CHANGES.md#103(franklin-feingold)
- [MISC] Added contributor information#100(jgrethe)
- [ENH] First(?) good practice recommendation. No excessive overrides in Inheritance principle#99(yarikoptic)
- [MISC] adding extensions page#97(choldgraf)
- [FIX] fix some urls (as detected to be broken/inconsistent)#95(yarikoptic)
- [MISC] Change BEP numbers to include MRS#94(Hboni)
- [FIX] harmonize and thus shorten templates etc#93(yarikoptic)
- [MISC] put links and some text into README#91(sappelhoff)
- [FIX] additional table to recap ’volume acquisition timing’#87(Remi-Gau)
- [FIX] Small typo in ”scanning sequence” DICOM Tag#84(Remi-Gau)
- [ENH] Added CBV contrast#82(TheChymera)
- [MISC] Add CC-BY 4.0 license#81(KirstieJane)
- [INFRA] Fix Travis break#80(franklin-feingold)
- [ENH] allow _dir for other EPI (func, dwi) sequences#78(yarikoptic)
- [MISC] Added appendix to mkdocs and added some internal links#77(franklin-feingold)
- [MISC] added JC Houde as contributor.#76(jchoude)


- [MISC] Updated my contributions#75(nicholst)
- [FIX] update HED appendix#74(sappelhoff)
- [FIX] unicode: replace greek mu and omega by micro and ohm signs#73(sappelhoff)
- [ENH] addce-\<label\>for fmri data#70(dasturge)
- [INFRA] pin pip version#68(chrisgorgo)
- [MISC] Fix link in index#46(chrisgorgo)
- [MISC] edit contributing guide#44(Park-Patrick)
- [INFRA] Mkdocs configuration and RTD setup#42(choldgraf)
- [MISC] Move definitions, compulsory, and raw/derivatives sections to principles#40(chrisgorgo)
- [MISC] Remove duplicate section#39(chrisgorgo)
- [INFRA] mkdocs rendering#36(chrisgorgo)
- [MISC] Style consistency#35(chrisgorgo)
- [MISC] Renaming files to conform with style guide#34(chrisgorgo)
- [INFRA] enable travis cache#32(chrisgorgo)
- [MISC] corrected link that is shown for CC0#31(robertoostenveld)
- [INFRA] added linter integration via travis#30(chrisgorgo)
- [MISC] Cleanup#29(chrisgorgo)
- [MISC] split intro, commons, mr, and meg into directory from specification.md#28(teonbrooks)
- [MISC] Add some bids starter kit contributors#27(KirstieJane)
- [MISC] Embedded footnotes into text#25(franklin-feingold)
- [MISC] Making HED Strategy Guide link prettier#24(fake-filo)
- [MISC] more cleanup#21(chrisgorgo)
- [MISC] formatted MEG (8.4)#17(franklin-feingold)
- [MISC] small fixes#16(chrisgorgo)
- [MISC] Add meg img#14(sappelhoff)
- [MISC] Cleaning up the specification#13(chrisgorgo)
- [MISC] Adding code of conduct#6(chrisgorgo)
- [INFRA] Renaming the main document#1(chrisgorgo)

### 1.1.1(2018-06-06)

- Improved the MEG landmark coordinates description.
- ReplacedManufacturersCapModelNameinmeg.jsonwithCapManufacturerandCapManufacturersModelName.
- RemoveEEGSamplingFrequencyandManufacturersAmplifierModelNamefrom themeg.json.
- Improved the behavioral data description.

### 1.1.0(2018-04-19)

- Added support for MEG data (merged BEP008).


- AddedSequenceNamefield.
- Added support for describing events with Hierarchical Event Descriptors: 4.3 Task events.
- AddedVolumeTimingandAcquisitionDurationfields: 4.1 Task (including resting state) imaging data.
- AddedDwellTimefield.

### 1.0.2(2017-07-18)

- Added support for high resolution (anatomical) T2star images: 4.1 Anatomy imaging data.
- Added support for multiple defacing masks: 4.1 Anatomy imaging data.
- Added optional key and metadata field for contrast enhanced structural scans: 4.1 Anatomy imaging data.
- AddedDelayTimefield: 4.1 Task (including resting state) imaging data.
- Added support for multi echo BOLD data: 4.1 Task (including resting state) imaging data.

### 1.0.1(2017-03-13)

- AddedInstitutionNamefield: 4.1 Task (including resting state) imaging data.
- AddedInstitutionAddressfield: 4.1 Task (including resting state) imaging data.
- AddedDeviceSerialNumberfield: 4.1 Task (including resting state) imaging data.
- AddedNumberOfVolumesDiscardedByUserandNumberOfVolumesDiscardedByScannerfield: 4.1 Task (including resting state) imaging data.
- AddedTotalReadoutTime tofunctional images metadata list: 4.1 Task (including resting state) imaging data.

### 1.0.1-rc1

- Added T1 Rho maps: 4.1 Anatomy imaging data.
- Added support for phenotypic information split into multiple files: 3.2 Participant key file.
- Added recommendations for multi site datasets.
- AddedSoftwareVersions.
- Addedrun-<run_index>to the phase encoding maps. Improved the description.
- AddedInversionTimemetadata key.
- Clarification on the source vs raw language.
- Addedtrial_typecolumn to the event files.
- Added missingsub-<participant_label>in behavioral data filenames.
- Added ability to store stimuli files.
- Clarified the language describing allowed subject labels.
- Added quantitative proton density maps.


### 1.0.0(2016-06-23)

- Added ability to specify fieldmaps acquired with multiple parameter sets.
- Added ability to have multiple runs of the same fieldmap.
- Added FLASH anatomical images.

### 1.0.0-rc4

- Replaced links to neurolex with explicit DICOM Tags.
- Added sourcedata.
- Added data dictionaries.
- Be more explicit about contents of JSON files for structural (anatomical) scans.

### 1.0.0-rc3

- RenamedPhaseEncodingDirectionvalues from ”x”, ”y”, ”z” to ”i”, ”j”, ”k” to avoid confusion with FSL parameters.
- RenamedSliceEncodingDirectionvalues from ”x”, ”y”, ”z” to ”i”, ”j”, ”k”.

### 1.0.0-rc2

- Removed the requirement that TSV files cannot include more than two consecutive spaces.
- Refactor of the definitions sections (copied from the manuscript).
- Make support for uncompressed.niifiles more explicit.
- AddedBIDSVersiontodataset.json.
- Remove the statement thatSliceEncodingDirectionis necessary for slice time correction.
- Changedicomconverterrecommendationfromdcmstacktodcm2niianddicm2niifollowinginteractionswiththecommunity(seehttps://github.com/moloney/dcm
    stack/issues/39andhttps://github.com/neurolabusc/dcm2niix/issues/4).
- Added section on behavioral experiments with no accompanying MRI acquisition.
- Add_magnitude.nii[.gz]image for GE type fieldmaps.
- Replaced EchoTimeDifference with EchoTime1 and EchoTime2 (SPM toolbox requires this input).
- Added support for single band reference image for DWI.
- Added DatasetDOI field in the dataset description.
- Added description of more metadata fields relevant to DWI fieldmap correction.
- PhaseEncodingDirection is now expressed in ”x”, ”y” etc. instead of ”PA” ”RL” for DWI scans (so it’s the same as BOLD scans).
- Addedrec-<label>flag to BOLD files to distinguish between different reconstruction algorithms (analogous to anatomical scans).
- Added recommendation to use_physiosuffix for continuous recordings of motion parameters obtained by the scanner side reconstruction algorithms.


### 1.0.0-rc1

- Initial release

* This Change Log was automatically generated bygithub_changelog_generator


