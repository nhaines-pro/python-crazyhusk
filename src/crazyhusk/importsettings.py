"""Wrapper objects for ImportAsset commandlet's ImportSettings JSON format."""

# Future Standard Library
from __future__ import annotations

# Standard Library
import json
import string
from dataclasses import asdict, dataclass, field, is_dataclass
from typing import ClassVar, List, Optional, Set


class UnrealImportError(Exception):
    """Custom exception representing errors encountered with ImportSettings."""


@dataclass
class ImportSettings(object):
    """Object wrapper representation of import settings passed to a UFactory via IImportSettingsParser."""

    def import_factory_name(self) -> Optional[str]:
        """Get the UFactory name to use for import. Use None to let the editor select the best one."""
        return None

    def default_groupname(self) -> str:
        """Get a default group name for import groups using this ImportSettings."""
        return "Import Unknown Type"

    def make_import_group(
        self,
        Filenames: List[str],
        DestinationPath: str,
        GroupName: Optional[str] = None,
        LevelToLoad: str = "",
        bReplaceExisting: bool = False,
        bSkipReadOnly: bool = False,
    ) -> ImportGroup:
        """Create an instance of ImportGroup using this ImportSettings."""
        return ImportGroup(
            Filenames=Filenames,
            DestinationPath=DestinationPath,
            GroupName=GroupName or self.default_groupname(),
            LevelToLoad=LevelToLoad,
            bReplaceExisting=bReplaceExisting,
            bSkipReadOnly=bSkipReadOnly,
            ImportSettings=self,
        )


@dataclass
class ImportGroup(object):
    """Object wrapper representation binding of ImportSettings to files, levels, and UFactory."""

    Filenames: List[str]
    DestinationPath: str
    GroupName: Optional[str] = None
    LevelToLoad: str = ""
    bReplaceExisting: bool = False
    bSkipReadOnly: bool = False
    ImportSettings: ImportSettings = ImportSettings()
    FactoryName: Optional[str] = field(init=False)

    def __post_init__(self) -> None:
        """Initialize additional dataclass fields and validate inputs."""
        if len(self.Filenames) == 0:
            raise UnrealImportError(
                "Import Groups must declare at least one filename for import."
            )
        if self.DestinationPath == "":
            raise UnrealImportError("Import Group DestinationPath must not be empty.")
        self.FactoryName = self.ImportSettings.import_factory_name()
        self.GroupName = self.GroupName or self.ImportSettings.default_groupname()


@dataclass
class CSVImportSettings(ImportSettings):
    """Object wrapper representation of ImportSettings for working with CSV and JSON data files as assets."""

    DEFAULT_GROUP_NAME: ClassVar[Optional[str]] = "Import CSV"
    CSV_IMPORT_TYPES: ClassVar[Set[str]] = {
        "ECSV_DataTable",
        "ECSV_CurveTable",
        "ECSV_CurveFloat",
        "ECSV_CurveVector",
        "ECSV_CurveLinearColor",
    }
    RICH_CURVE_INTERPOLATION_MODES: ClassVar[Set[str]] = {
        "RCIM_Linear",
        "RCIM_Constant",
        "RCIM_Cubic",
        "RCIM_None",
    }

    ImportRowStruct: str = ""
    ImportType: str = "ECSV_CurveTable"
    ImportCurveInterpMode: str = "RCIM_Linear"

    def __post_init__(self) -> None:
        """Initialize additional dataclass fields and validate inputs."""
        if self.ImportType not in CSVImportSettings.CSV_IMPORT_TYPES:
            raise UnrealImportError(f"ImportType {self.ImportType} is not supported.")
        if (
            self.ImportCurveInterpMode
            not in CSVImportSettings.RICH_CURVE_INTERPOLATION_MODES
        ):
            raise UnrealImportError(
                f"Interpolation Mode {self.ImportCurveInterpMode} is not supported."
            )
        if self.ImportType == "ECSV_DataTable":
            if self.ImportRowStruct == "":
                raise UnrealImportError(
                    "ImportRowStruct must not be empty for DataTable import."
                )
            elif not self.ImportRowStruct.startswith("/"):
                raise UnrealImportError(
                    f"Import Row Struct must be a Unral-style path: {self.ImportRowStruct}"
                )

    def import_factory_name(self) -> Optional[str]:
        """Get the UFactory name to use for import. Use None to let the editor select the best one."""
        return "CSVImportFactory"

    def default_groupname(self) -> str:
        """Get a default group name for import groups using this ImportSettings."""
        return f"Import CSV {self.ImportType.split('ECSV_')[-1]}"


@dataclass
class FbxAssetImportData(object):
    """Object wrapper representation of UFbxAssetImportData."""

    # ImportTranslation: Vector
    # ImportRotation: Rotator
    ImportUniformScale: float = 1.0
    bConvertScene: bool = True
    bForceFrontXAxis: bool = False
    bConvertSceneUnit: bool = False
    bImportAsScene: bool = False


@dataclass
class FbxMeshImportData(FbxAssetImportData):
    """Object wrapper representation of UFbxMeshImportData."""

    NORMAL_IMPORT_METHODS: ClassVar[Set[str]] = {
        "FBXNIM_ComputeNormals",
        "FBXNIM_ImportNormals",
        "FBXNIM_ImportNormalsAndTangents",
    }
    NORMAL_GENERATION_METHODS: ClassVar[Set[str]] = {
        "BuiltIn",
        "MikkTSpace",
    }
    VERTEX_COLOR_IMPORT_OPTIONS: ClassVar[Set[str]] = {
        "Replace",
        "Ignore",
        "Override",
    }

    bTransformVertexToAbsolute: bool = False
    bBakePivotInVertex: bool = False
    bImportMeshLODs: bool = True
    NormalImportMethod: str = "FBXNIM_ComputeNormals"
    NormalGenerationMethod: str = "BuiltIn"
    bComputeWeightedNormals: bool = True
    bReorderMaterialToFbxOrder: bool = False

    def __post_init__(self) -> None:
        """Initialize additional dataclass fields and validate inputs."""
        if self.NormalImportMethod not in FbxMeshImportData.NORMAL_IMPORT_METHODS:
            raise UnrealImportError(
                f"NormalImportMethod {self.NormalImportMethod} is not supported."
            )
        if (
            self.NormalGenerationMethod
            not in FbxMeshImportData.NORMAL_GENERATION_METHODS
        ):
            raise UnrealImportError(
                f"NormalGenerationMethod {self.NormalGenerationMethod} is not supported."
            )


@dataclass
class FbxStaticMeshImportData(FbxMeshImportData):
    """Object wrapper representation of UFbxStaticMeshImportData."""

    StaticMeshLODGroup: str = ""
    VertexColorImportOption: str = "Replace"
    VertexOverrideColor: str = "FFF"
    bRemoveDegenerates: bool = True
    bBuildAdjacencyBuffer: bool = True
    bBuildReversedIndexBuffer: bool = True
    bGenerateLightmapUVs: bool = True
    bOneConvexHullPerUCX: bool = True
    bAutoGenerateCollision: bool = True
    bCombineMeshes: bool = True

    def __post_init__(self) -> None:
        """Initialize additional dataclass fields and validate inputs."""
        if (
            self.VertexColorImportOption
            not in FbxMeshImportData.VERTEX_COLOR_IMPORT_OPTIONS
        ):
            raise UnrealImportError(
                f"VertexColorImportOption {self.VertexColorImportOption} is not supported."
            )
        if not all(c in string.hexdigits for c in self.VertexOverrideColor):
            raise UnrealImportError(
                f"VertexOverrideColor {self.VertexOverrideColor} is not valid hexadecimal string."
            )


@dataclass
class FbxSkeletalMeshImportData(FbxMeshImportData):
    """Object wrapper representation of UFbxSkeletalMeshImportData."""

    FBX_IMPORT_CONTENT_TYPES: ClassVar[Set[str]] = {
        "FBXICT_All",
        "FBXICT_Geometry",
        "FBXICT_SkinningWeights",
    }

    bTransformVertexToAbsolute: bool = True
    ImportContentType: str = "FBXICT_All"
    LastImportContentType: str = "FBXICT_All"
    bUpdateSkeletonReferencePose: bool = True
    bUseT0AsRefPose: bool = True
    bPreserveSmoothingGroups: bool = True
    bImportMeshesInBoneHierarchy: bool = True
    bImportMorphTargets: bool = True
    ThresholdPosition: float = 0.0
    ThresholdTangentNormal: float = 0.0
    ThresholdUV: float = 0.0
    MorphThresholdPosition: float = 0.0

    def __post_init__(self) -> None:
        """Initialize additional dataclass fields and validate inputs."""
        if (
            self.ImportContentType
            not in FbxSkeletalMeshImportData.FBX_IMPORT_CONTENT_TYPES
        ):
            raise UnrealImportError(
                f"ImportContentType {self.ImportContentType} is not supported."
            )
        if (
            self.LastImportContentType
            not in FbxSkeletalMeshImportData.FBX_IMPORT_CONTENT_TYPES
        ):
            raise UnrealImportError(
                f"LastImportContentType {self.LastImportContentType} is not supported."
            )


@dataclass
class FbxAnimSequenceImportData(FbxAssetImportData):
    """Object wrapper representation of UFbxAnimSequenceImportData."""

    FBX_ANIMATION_LENGTH_IMPORT_TYPES: ClassVar[Set[str]] = {
        "FBXALIT_ExportedTime",
        "FBXALIT_AnimatedKey",
        "FBXALIT_SetRange",
    }

    bImportMeshesInBoneHierarchy: bool = False
    AnimationLength: str = "FBXALIT_ExportedTime"
    # FrameImportRange: FInt32Interval
    bUseDefaultSampleRate: bool = False
    CustomSampleRate: int = 0
    SourceAnimationName: str = ""
    bImportCustomAttribute: bool = True
    bDeleteExistingCustomAttributeCurves: bool = False
    bDeleteExistingNonCurveCustomAttributes: bool = False
    bImportBoneTracks: bool = True
    bSetMaterialDriveParameterOnCustomAttribute: bool = False
    MaterialCurveSuffixes: List[str] = field(default_factory=list)
    bRemoveRedundantKeys: bool = True
    bDeleteExistingMorphTargetCurves: bool = False
    bDoNotImportCurveWithZero: bool = True
    bPreserveLocalTransform: bool = False

    def __post_init__(self) -> None:
        """Initialize additional dataclass fields and validate inputs."""
        if (
            self.AnimationLength
            not in FbxAnimSequenceImportData.FBX_ANIMATION_LENGTH_IMPORT_TYPES
        ):
            raise UnrealImportError(
                f"AnimationLength {self.AnimationLength} is not supported."
            )


@dataclass
class FbxTextureImportData(FbxAssetImportData):
    """Object wrapper representation of UFbxTextureImportData."""

    FBX_MATERIAL_SEARCH_LOCATIONS: ClassVar[Set[str]] = {
        "Local",
        "UnderParent",
        "UnderRoot",
        "AllAssets",
        "DoNotSearch",
    }

    bInvertNormalMaps: bool = True
    MaterialSearchLocation: str = "Local"
    BaseMaterialName: str = ""
    BaseColorName: str = ""
    BaseDiffuseTextureName: str = ""
    BaseNormalTextureName: str = ""
    BaseEmissiveColorName: str = ""
    BaseEmmisiveTextureName: str = ""
    BaseSpecularTextureName: str = ""
    BaseOpacityTextureName: str = ""

    def __post_init__(self) -> None:
        """Initialize additional dataclass fields and validate inputs."""
        if (
            self.MaterialSearchLocation
            not in FbxTextureImportData.FBX_MATERIAL_SEARCH_LOCATIONS
        ):
            raise UnrealImportError(
                f"MaterialSearchLocation {self.MaterialSearchLocation} is not supported."
            )


@dataclass
class FBXImportSettings(ImportSettings):
    """Object wrapper representation of import settings used to create assets from FBX or OBJ files."""

    FBX_IMPORT_TYPES: ClassVar[Set[str]] = {
        "FBXIT_StaticMesh",
        "FBXIT_SkeletalMesh",
        "FBXIT_Animation",
    }

    bIsObjImport: bool = False
    OriginalImportType: str = "FBXIT_StaticMesh"
    MeshTypeToImport: str = "FBXIT_StaticMesh"
    bOverrideFullName: bool = True
    bImportAsSkeletal: bool = False
    bImportMesh: bool = False
    Skeleton: str = ""
    bCreatePhysicsAsset: bool = True
    PhysicsAsset: str = ""
    bAutoComputeLodDistances: bool = True
    LodDistance0: float = 0.0
    LodDistance1: float = 0.0
    LodDistance2: float = 0.0
    LodDistance3: float = 0.0
    LodDistance4: float = 0.0
    LodDistance5: float = 0.0
    LodDistance6: float = 0.0
    LodDistance7: float = 0.0
    MinimumLodNumber: int = 0
    LodNumber: int = 0
    bImportAnimations: bool = True
    OverrideAnimationName: str = ""
    bImportRigidMesh: bool = True
    bImportMaterials: bool = True
    bImportTextures: bool = True
    bResetToFbxOnMaterialConflict: bool = True
    StaticMeshImportData: FbxStaticMeshImportData = FbxStaticMeshImportData()
    SkeletalMeshImportData: FbxSkeletalMeshImportData = FbxSkeletalMeshImportData()
    AnimSequenceImportData: FbxAnimSequenceImportData = FbxAnimSequenceImportData()
    TextureImportData: FbxTextureImportData = FbxTextureImportData()
    bAutomatedImportShouldDetectType: bool = False

    def __post_init__(self) -> None:
        """Initialize additional dataclass fields and validate inputs."""
        if self.OriginalImportType not in FBXImportSettings.FBX_IMPORT_TYPES:
            raise UnrealImportError(
                f"OriginalImportType {self.OriginalImportType} is not supported."
            )
        if self.MeshTypeToImport not in FBXImportSettings.FBX_IMPORT_TYPES:
            raise UnrealImportError(
                f"MeshTypeToImport {self.MeshTypeToImport} is not supported."
            )

    def import_factory_name(self) -> Optional[str]:
        """Get the UFactory name to use for import. Use None to let the editor select the best one."""
        return "FbxFactory"

    def default_groupname(self) -> str:
        """Get a default group name for import groups using this ImportSettings."""
        return f"Import FBX"


def import_groups_to_json(
    *import_groups: ImportGroup, indent: Optional[int] = None
) -> str:
    """Serialize instances of ImportGroup to JSON for use by UImportAssetsCommandlet."""
    return json.dumps(
        {
            "ImportGroups": [
                asdict(group) for group in import_groups if is_dataclass(group)
            ]
        },
        indent=indent,
    )
