# -*- coding: utf-8 -*-

from bases import *

# ##########################################################################
# datatypes
# ##########################################################################

DT = str
DTM = str
GTS = str
ID = str
IS = str
NM = str
SI = str
ST = str
TM = str
var = str # т.к. я не нашёл определения типа var


class CNN(THl7Compound):
    _items = [ ('CNN_1', 'CNN.1', ID),      # ID Number
               ('CNN_2', 'CNN.2', ST),      # Family Name
               ('CNN_3', 'CNN.3', ST),      # Given Name
               ('CNN_4', 'CNN.4', ST),      # Second and Further Given Names or Initials Thereof
               ('CNN_5', 'CNN.5', ST),      # Suffix (e.g., JR or III)
               ('CNN_6', 'CNN.6', ST),      # Prefix (e.g., DR)
               ('CNN_7', 'CNN.7', ID),      # Degree (e.g., MD) {HL70360}
               ('CNN_8', 'CNN.8', IS),      # Source Table {HL70297}
               ('CNN_9', 'CNN.9', IS),      # Assigning Authority - Namespace ID {HL70363}
               ('CNN_10', 'CNN.10', ST),    # Assigning Authority - Universal ID
               ('CNN_11', 'CNN.11', ID),    # Assigning Authority - Universal ID Type {HL70301}
             ]


class MO(THl7Compound):
    _items = [ ('MO_1', 'MO.1', NM),        # Quantity
               ('MO_2', 'MO.2', ID),        # Denomination
             ]


class TS(THl7Compound):
    _items = [ ('TS_1', 'TS.1', DTM),       # Time
               ('TS_2', 'TS.2', ID),        # Degree of Precision {HL70529}
             ]


class TX(THl7Compound):
    _items = [ ('escape', 'escape', [str]),
             ]
# or TX = str ?

class HD(THl7Compound):
    _items = [ ('HD_1', 'HD.1', IS),        # Namespace ID {HL70300}
               ('HD_2', 'HD.2', ST),        # Universal ID
               ('HD_3', 'HD.3', ID),        # Universal ID Type {HL70301}
             ]


# ##########################################################################
# fields & complex datatypes
# ##########################################################################

class AD(THl7Compound):
    _items = [ ('AD_1', 'AD.1', ST),    # Street Address
               ('AD_2', 'AD.2', ST),    # Other Designation
               ('AD_3', 'AD.3', ST),    # City
               ('AD_4', 'AD.4', ST),    # State or Province
               ('AD_5', 'AD.5', ST),    # Zip or Postal Code
               ('AD_6', 'AD.6', ID),    # Country {HL70399}
               ('AD_7', 'AD.7', ID),    # Address Type {HL70190}
               ('AD_8', 'AD.8', ST),    # Other Geographic Designation
             ]


class CE(THl7Compound):
    _items = [ ('CE_1', 'CE.1', str),
               ('CE_2', 'CE.2', str),
               ('CE_3', 'CE.3', str),
               ('CE_4', 'CE.4', str),
               ('CE_5', 'CE.5', str),
               ('CE_6', 'CE.6', str),
             ]

class CNE(THl7Compound):
    _items = [ ('CNE_1', 'CNE.1', ST),  # Identifier
               ('CNE_2', 'CNE.2', ST),  # Text
               ('CNE_3', 'CNE.3', ID),  # Name of Coding System {HL70396}
               ('CNE_4', 'CNE.4', ST),  # Alternate Identifier
               ('CNE_5', 'CNE.5', ST),  # Alternate Text
               ('CNE_6', 'CNE.6', ID),  # Name of Alternate Coding System {HL70396}
               ('CNE_7', 'CNE.7', ST),  # Coding System Version ID
               ('CNE_8', 'CNE.8', ST),  # Alternate Coding System Version ID
               ('CNE_9', 'CNE.9', ST),  # Original Text
             ]


class CWE(THl7Compound):
    _items = [ ('CWE_1', 'CWE.1', str),
               ('CWE_2', 'CWE.2', str),
               ('CWE_3', 'CWE.3', str),
               ('CWE_4', 'CWE.4', str),
               ('CWE_5', 'CWE.5', str),
               ('CWE_6', 'CWE.6', str),
               ('CWE_7', 'CWE.7', str),
               ('CWE_8', 'CWE.8', str),
               ('CWE_9', 'CWE.9', str),
             ]


class CP(THl7Compound):
    _items = [ ('CP_1', 'CP.1', MO),        # Price
               ('CP_2', 'CP.2', ID),        # Price Type {HL70205}
               ('CP_3', 'CP.3', NM),        # From Value
               ('CP_4', 'CP.4', NM),        # To Value
               ('CP_5', 'CP.5', CE),        # Range Units
               ('CP_6', 'CP.6', ID),        # Range Type {HL70298}
             ]


class CQ(THl7Compound):
    _items = [ ('CQ_1', 'CQ.1', NM),        # Quantity
               ('CQ_2', 'CQ.2', CE),        # Units
             ]

class CX(THl7Compound):
    _items = [ ('CX_1', 'CX.1', ST),        # ID Number
               ('CX_2', 'CX.2', ST),        # Check Digit
               ('CX_3', 'CX.3', ID),        # Check Digit Scheme {HL70061}
               ('CX_4', 'CX.4', HD),        # Assigning Authority {HL70363}
               ('CX_5', 'CX.5', ID),        # Identifier Type Code {HL70203}
               ('CX_6', 'CX.6', HD),        # Assigning Facility
               ('CX_7', 'CX.7', DT),        # Effective Date
               ('CX_8', 'CX.8', DT),        # Expiration Date
               ('CX_9', 'CX.9', CWE),       # Assigning Jurisdiction
               ('CX_10', 'CX.10', CWE),     # Assigning Agency or Department
             ]


class DLD(THl7Compound):
    _items = [ ('DLD_1', 'DLD.1', IS),      # Discharge Location {HL70113}
               ('DLD_2', 'DLD.2', TS),      # Effective Date
             ]


class DR(THl7Compound):
    _items = [ ('DR_1', 'DR.1', TS),        # Range Start Date/Time
               ('DR_2', 'DR.2', TS),        # Range End Date/Time
             ]


class EI(THl7Compound):
    _items = [ ('EI_1', 'EI.1', ST),        # Entity Identifier
               ('EI_2', 'EI.2', IS),        # Namespace ID {HL70363}
               ('EI_3', 'EI.3', ST),        # Universal ID
               ('EI_4', 'EI.4', ID),        # Universal ID Type {HL70301}
             ]


class EIP(THl7Compound):
    _items = [ ('EIP_1', 'EIP.1', EI),      # Placer Assigned Identifier
               ('EIP_2', 'EIP.2', EI),      # Filler Assigned Identifier
             ]


class ELD(THl7Compound):
    _items = [ ('ELD_1', 'ELD.1', str),
               ('ELD_2', 'ELD.2', str),
               ('ELD_3', 'ELD.3', str),
               ('ELD_4', 'ELD.4', str),
             ]


class ERL(THl7Compound):
    _items = [ ('ERL_1', 'ERL.1', str),
               ('ERL_2', 'ERL.2', str),
               ('ERL_3', 'ERL.3', str),
               ('ERL_4', 'ERL.4', str),
               ('ERL_5', 'ERL.5', str),
               ('ERL_6', 'ERL.6', str),
             ]


class FC(THl7Compound):
    _items = [ ('FC_1', 'FC.1', IS),        # Financial Class Code {HL70064}
               ('FC_2', 'FC.2', TS),        # Effective Date
             ]


class FN(THl7Compound):
    _items = [ ('FN_1', 'FN.1', ST),        # Surname
               ('FN_2', 'FN.2', ST),        # Own Surname Prefix
               ('FN_3', 'FN.3', ST),        # Own Surname
               ('FN_4', 'FN.4', ST),        # Surname Prefix From Partner/Spouse
               ('FN_5', 'FN.5', ST),        # Surname From Partner/Spouse
             ]


class FT(THl7Compound):
    _items = [ ('escape', 'escape', [str]),
             ]
# or FT = str ?


class JCC(THl7Compound):
    _items = [ ('JCC_1', 'JCC.1', IS),      # Job Code {HL70327}
               ('JCC_2', 'JCC.2', IS),      # Job Class {HL70328}
               ('JCC_3', 'JCC.3', TX),      # Job Description Text
             ]

class LA1(THl7Compound):
    _items = [ ('LA1_1', 'LA1.1', IS),      # Point of Care
               ('LA1_2', 'LA1.2', IS),      # Room
               ('LA1_3', 'LA1.3', IS),      # Bed
               ('LA1_4', 'LA1.4', HD),      # Facility
               ('LA1_5', 'LA1.5', IS),      # Location Status
               ('LA1_6', 'LA1.6', IS),      # Patient Location Type
               ('LA1_7', 'LA1.7', IS),      # Building
               ('LA1_8', 'LA1.8', IS),      # Floor
               ('LA1_9', 'LA1.9', AD),      # Address
             ]


class MOC(THl7Compound):
    _items = [ ('MOC_1', 'MOC.1', MO),      # Monetary Amount
               ('MOC_2', 'MOC.2', str),     # Charge Code
             ]


class MSG(THl7Compound):
    _items = [ ('MSG_1', 'MSG.1', str),
               ('MSG_2', 'MSG.2', str),
               ('MSG_3', 'MSG.3', str),
             ]


class NDL(THl7Compound):
    _items = [ ('NDL_1', 'NDL.1', CNN),     # Name
               ('NDL_2', 'NDL.2', TS),      # Start Date/time
               ('NDL_3', 'NDL.3', TS),      # End Date/time
               ('NDL_4', 'NDL.4', IS),      # Point of Care {HL70302}
               ('NDL_5', 'NDL.5', IS),      # Room {HL70303}
               ('NDL_6', 'NDL.6', IS),      # Bed {HL70304}
               ('NDL_7', 'NDL.7', HD),      # Facility
               ('NDL_8', 'NDL.8', IS),      # Location Status {HL70306}
               ('NDL_9', 'NDL.9', IS),      # Patient Location Type {HL70305}
               ('NDL_10', 'NDL.10', IS),    # Building {HL70307}
               ('NDL_11', 'NDL.11', IS),    # Floor {HL70308}
             ]


class OSD(THl7Compound):
    _items = [ ('OSD_1', 'OSD.1', ID),      # Sequence/Results Flag {HL70524}
               ('OSD_2', 'OSD.2', ST),      # Placer Order Number: Entity Identifier
               ('OSD_3', 'OSD.3', IS),      # Placer Order Number: Namespace ID {HL70363}
               ('OSD_4', 'OSD.4', ST),      # Filler Order Number: Entity Identifier
               ('OSD_5', 'OSD.5', IS),      # Filler Order Number: Namespace ID {HL70363}
               ('OSD_6', 'OSD.6', ST),      # Sequence Condition Value
               ('OSD_7', 'OSD.7', NM),      # Maximum Number of Repeats
               ('OSD_8', 'OSD.8', ST),      # Placer Order Number: Universal ID
               ('OSD_9', 'OSD.9', ID),      # Placer Order Number: Universal ID Type {HL70301}
               ('OSD_10', 'OSD.10', ST),    # Filler Order Number: Universal ID
               ('OSD_11', 'OSD.11', ID),    # Filler Order Number: Universal ID Type {HL70301}
             ]


class PL(THl7Compound):
    _items = [ ('PL_1', 'PL.1', IS),        # Point of Care {HL70302}
               ('PL_2', 'PL.2', IS),        # Room {HL70303}
               ('PL_3', 'PL.3', IS),        # Bed {HL70304}
               ('PL_4', 'PL.4', HD),        # Facility
               ('PL_5', 'PL.5', IS),        # Location Status {HL70306}
               ('PL_6', 'PL.6', IS),        # Person Location Type {HL70305}
               ('PL_7', 'PL.7', IS),        # Building {HL70307}
               ('PL_8', 'PL.8', IS),        # Floor {HL70308}
               ('PL_9', 'PL.9', ST),        # Location Description
               ('PL_10', 'PL.10', EI),      # Comprehensive Location Identifier
               ('PL_11', 'PL.11', HD),      # Assigning Authority for Location
             ]


class PLN(THl7Compound):
    _items = [ ('PLN_1', 'PLN.1', ST),      # ID Number
               ('PLN_2', 'PLN.2', IS),      # Type of ID Number {HL70338}
               ('PLN_3', 'PLN.3', ST),      # State/other Qualifying Information
               ('PLN_4', 'PLN.4', DT),      # Expiration Date
             ]

class PRL(THl7Compound):
    _items = [ ('PRL_1', 'PRL.1', CE),      # Parent Observation Identifier
               ('PRL_2', 'PRL.2', ST),      # Parent Observation Sub-identifier
               ('PRL_3', 'PRL.3', TX),      # Parent Observation Value Descriptor
             ]


class PT(THl7Compound):
    _items = [ ('PT_1', 'PT.1', str),
               ('PT_2', 'PT.2', str),
             ]


class RI(THl7Compound):
    _items = [ ('RI_1', 'RI.1', IS),        # Repeat Pattern {HL70335}
               ('RI_2', 'RI.2', ST),        # Explicit Time Interval
             ]


class RPT(THl7Compound):
    _items = [ ('RPT_1', 'RPT.1', CWE),     # Repeat Pattern Code {HL70335}
               ('RPT_2', 'RPT.2', ID),      # Calendar Alignment {HL70527}
               ('RPT_3', 'RPT.3', NM),      # Phase Range Begin Value
               ('RPT_4', 'RPT.4', NM),      # Phase Range End Value
               ('RPT_5', 'RPT.5', NM),      # Period Quantity
               ('RPT_6', 'RPT.6', IS),      # Period Units
               ('RPT_7', 'RPT.7', ID),      # Institution Specified Time {HL70136}
               ('RPT_8', 'RPT.8', ID),      # Event {HL70528}
               ('RPT_9', 'RPT.9', NM),      # Event Offset Quantity
               ('RPT_10', 'RPT.10', IS),    # Event Offset Units
               ('RPT_11', 'RPT.11', GTS),   # General Timing Specification
             ]


class SAD(THl7Compound):
    _items = [ ('SAD_1', 'SAD.1', ST),      # Street or Mailing Address
               ('SAD_2', 'SAD.2', ST),      # Street Name
               ('SAD_3', 'SAD.3', ST),      # Dwelling Number
             ]


class SPS(THl7Compound):
    _items = [ ('SPS_1', 'SPS.1', CWE),     # Specimen Source Name or Code
               ('SPS_2', 'SPS.2', CWE),     # Additives {HL70371}
               ('SPS_3', 'SPS.3', TX),      # Specimen Collection Method
               ('SPS_4', 'SPS.4', CWE),     # Body Site {HL70163}
               ('SPS_5', 'SPS.5', CWE),     # Site Modifier {HL70495}
               ('SPS_6', 'SPS.6', CWE),     # Collection Method Modifier Code
               ('SPS_7', 'SPS.7', CWE),     # Specimen Role {HL70369}
             ]


class TQ(THl7Compound):
    _items = [ ('TQ_1', 'TQ.1', CQ),        # Quantity
               ('TQ_2', 'TQ.2', RI),        # Interval
               ('TQ_3', 'TQ.3', ST),        # Duration
               ('TQ_4', 'TQ.4', TS),        # Start Date/Time
               ('TQ_5', 'TQ.5', TS),        # End Date/Time
               ('TQ_6', 'TQ.6', ST),        # Priority
               ('TQ_7', 'TQ.7', ST),        # Condition
               ('TQ_8', 'TQ.8', TX),        # Text
               ('TQ_9', 'TQ.9', ID),        # Conjunction {HL70472}
               ('TQ_10', 'TQ.10', OSD),     # Order Sequencing
               ('TQ_11', 'TQ.11', CE),      # Occurrence Duration
               ('TQ_12', 'TQ.12', NM),      # Total Occurrences
             ]


class VID(THl7Compound):
    _items = [ ('VID_1', 'VID.1', str, '2.5'),
               ('VID_2', 'VID.2', str),
               ('VID_3', 'VID.3', str),
             ]

class XAD(THl7Compound):
    _items = [ ('XAD_1', 'XAD.1', SAD),     # Street Address
               ('XAD_2', 'XAD.2', ST),      # Other Designation
               ('XAD_3', 'XAD.3', ST),      # City
               ('XAD_4', 'XAD.4', ST),      # State or Province
               ('XAD_5', 'XAD.5', ST),      # Zip or Postal Code
               ('XAD_6', 'XAD.6', ID),      # Country {HL70399}
               ('XAD_7', 'XAD.7', ID),      # Address Type {HL70190}
               ('XAD_8', 'XAD.8', ST),      # Other Geographic Designation
               ('XAD_9', 'XAD.9', IS),      # County/Parish Code {HL70289}
               ('XAD_10', 'XAD.10', IS),    # Census Tract {HL70288}
               ('XAD_11', 'XAD.11', ID),    # Address Representation Code {HL70465}
               ('XAD_12', 'XAD.12', DR),    # Address Validity Range
               ('XAD_13', 'XAD.13', TS),    # Effective Date
               ('XAD_14', 'XAD.14', TS),    # Expiration Date
             ]


class XCN(THl7Compound):
    _items = [ ('XCN_1', 'XCN.1', ST),      # ID Number
               ('XCN_2', 'XCN.2', FN),      # Family Name
               ('XCN_3', 'XCN.3', ST),      # Given Name
               ('XCN_4', 'XCN.4', ST),      # Second and Further Given Names or Initials Thereof
               ('XCN_5', 'XCN.5', ST),      # Suffix (e.g., JR or III)
               ('XCN_6', 'XCN.6', ST),      # Prefix (e.g., DR)
               ('XCN_7', 'XCN.7', ID),      # Degree (e.g., MD) {HL70360}
               ('XCN_8', 'XCN.8', IS),      # Source Table {HL70297}
               ('XCN_9', 'XCN.9', HD),      # Assigning Authority
               ('XCN_10', 'XCN.10', ID),    # Name Type Code {HL70200}
               ('XCN_11', 'XCN.11', ST),    # Identifier Check Digit
               ('XCN_12', 'XCN.12', ID),    # Check Digit Scheme {HL70061}
               ('XCN_13', 'XCN.13', ID),    # Identifier Type Code {HL70203}
               ('XCN_14', 'XCN.14', HD),    # Assigning Facility
               ('XCN_15', 'XCN.15', IS),    # Name Representation Code {HL70465}
               ('XCN_16', 'XCN.16', CE),    # Name Context {HL70448}
               ('XCN_17', 'XCN.17', DR),    # Name Validity Range
               ('XCN_18', 'XCN.18', ID),    # Name Assembly Order (HL70444)
               ('XCN_19', 'XCN.19', TS),    # Effective Date
               ('XCN_20', 'XCN.20', TS),    # Expiration Date
               ('XCN_21', 'XCN.21', ST),    # Professional Suffix
               ('XCN_22', 'XCN.22', CWE),   # Assigning Jurisdiction
               ('XCN_23', 'XCN.23', CWE),   # Assigning Agency or Department
             ]


class XPN(THl7Compound):
    _items = [ ('XPN_1', 'XPN.1', FN),      # Family Name
               ('XPN_2', 'XPN.2', ST),      # Given Name
               ('XPN_3', 'XPN.3', ST),      # Second and Further Given Names or Initials Thereof
               ('XPN_4', 'XPN.4', ST),      # Suffix (e.g., JR or III)
               ('XPN_5', 'XPN.5', ST),      # Prefix (e.g., DR)
               ('XPN_6', 'XPN.6', ID),      # Degree (e.g., MD) {HL70360}
               ('XPN_7', 'XPN.7', ID),      # Name Type Code {HL70200}
               ('XPN_8', 'XPN.8', ID),      # Name Representation Code {HL70465}
               ('XPN_9', 'XPN.9', CE),      # Name Context {HL70448}
               ('XPN_10', 'XPN.10', DR),    # Name Validity Range
               ('XPN_11', 'XPN.11', ID),    # Name Assembly Order {HL70444}
               ('XPN_12', 'XPN.12', TS),    # Effective Date
               ('XPN_13', 'XPN.13', TS),    # Expiration Date
               ('XPN_14', 'XPN.14', ST),    # Professional Suffix
             ]


class XON(THl7Compound):
    _items = [ ('XON_1', 'XON.1', str),
               ('XON_2', 'XON.2', str),
               ('XON_3', 'XON.3', str),
               ('XON_4', 'XON.4', str),
               ('XON_5', 'XON.5', str),
               ('XON_6', 'XON.6', str),
               ('XON_7', 'XON.7', str),
               ('XON_8', 'XON.8', str),
               ('XON_9', 'XON.9', str),
               ('XON_10', 'XON.10', str),
             ]


class XTN(THl7Compound):
    _items = [ ('XTN_1', 'XTN.1', str),
               ('XTN_2', 'XTN.2', str),
               ('XTN_3', 'XTN.3', str),
               ('XTN_4', 'XTN.4', str),
               ('XTN_5', 'XTN.5', str),
               ('XTN_6', 'XTN.6', str),
               ('XTN_7', 'XTN.7', str),
               ('XTN_8', 'XTN.8', str),
               ('XTN_9', 'XTN.9', str),
               ('XTN_10', 'XTN.10', str),
               ('XTN_11', 'XTN.11', str),
               ('XTN_12', 'XTN.12', str),
             ]


# ##########################################################################
# segments
# ##########################################################################

class CTD(THl7Compound):
    _items = [ ('CTD_1', 'CTD.1', [CE]),    # Contact Role {HL70131}
               ('CTD_2', 'CTD.2', [XPN]),   # Contact Name
               ('CTD_3', 'CTD.3', [XAD]),   # Contact Address
               ('CTD_4', 'CTD.4', PL),      # Contact Location
               ('CTD_5', 'CTD.5', [XTN]),   # Contact Communication Information
               ('CTD_6', 'CTD.6', CE),      # Preferred Method of Contact {HL70185}
               ('CTD_7', 'CTD.7', [PLN]),   # Contact Identifiers
             ]


class CTI(THl7Compound):
    _items = [ ('CTI_1', 'CTI.1', EI),      # Sponsor Study ID
               ('CTI_2', 'CTI.2', CE),      # Study Phase Identifier
               ('CTI_3', 'CTI.3', CE),      # Study Scheduled Time Point
             ]


class DSC(THl7Compound):
    _items = [ ('DSC_1', 'DSC.1', ST),      # Continuation Pointer
               ('DSC_2', 'DSC.2', ID),      # Continuation Style {HL70398}
             ]


class FT1(THl7Compound):
    _items = [ ('FT1_1', 'FT1.1', SI),      # Set ID - FT1
               ('FT1_2', 'FT1.2', ST),      # Transaction ID
               ('FT1_3', 'FT1.3', ST),      # Transaction Batch ID
               ('FT1_4', 'FT1.4', DR),      # Transaction Date
               ('FT1_5', 'FT1.5', TS),      # Transaction Posting Date
               ('FT1_6', 'FT1.6', IS),      # Transaction Type {HL70017}
               ('FT1_7', 'FT1.7', CE),      # Transaction Code {HL70132}
               ('FT1_8', 'FT1.8', ST),      # Transaction Description
               ('FT1_9', 'FT1.9', ST),      # Transaction Description - Alt
               ('FT1_10', 'FT1.10', NM),    # Transaction Quantity
               ('FT1_11', 'FT1.11', CP),    # Transaction Amount - Extended
               ('FT1_12', 'FT1.12', CP),    # Transaction Amount - Unit
               ('FT1_13', 'FT1.13', CE),    # Department Code {HL70049}
               ('FT1_14', 'FT1.14', CE),    # Insurance Plan ID {HL70072}
               ('FT1_15', 'FT1.15', CP),    # Insurance Amount
               ('FT1_16', 'FT1.16', PL),    # Assigned Patient Location
               ('FT1_17', 'FT1.17', IS),    # Fee Schedule {HL70024}
               ('FT1_18', 'FT1.18', IS),    # Patient Type {HL70018}
               ('FT1_19', 'FT1.19', [CE]),  # Diagnosis Code - FT1 {HL70051}
               ('FT1_20', 'FT1.20', [XCN]), # Performed By Code {HL70084}
               ('FT1_21', 'FT1.21', [XCN]), # Ordered By Code
               ('FT1_22', 'FT1.22', CP),    # Unit Cost
               ('FT1_23', 'FT1.23', EI),    # Filler Order Number
               ('FT1_24', 'FT1.24', [XCN]), # Entered By Code
               ('FT1_25', 'FT1.25', CE),    # Procedure Code {HL70088}
               ('FT1_26', 'FT1.26', [CE]),  # Procedure Code Modifier {HL70340}
               ('FT1_27', 'FT1.27', CE),    # Advanced Beneficiary Notice Code {HL70339}
               ('FT1_28', 'FT1.28', CWE),   # Medically Necessary Duplicate Procedure Reason. {HL70476}
               ('FT1_29', 'FT1.29', CNE),   # NDC Code {HL70549}
               ('FT1_30', 'FT1.30', CX),    # Payment Reference ID
               ('FT1_31', 'FT1.31', [SI]),  # Transaction Reference Key
             ]


class MSH(THl7Compound):
    _items = [ ('MSH_1', 'MSH.1', str, '|'),            # Field Separator
               ('MSH_2', 'MSH.2', str, '^~\\&'),        # Encoding Characters
               ('MSH_3', 'MSH.3', HD),                  # Sending Application
               ('MSH_4', 'MSH.4', HD),                  # Sending Facility
               ('MSH_5', 'MSH.5', HD),                  # Receiving Application
               ('MSH_6', 'MSH.6', HD),                  # Receiving Facility
               ('MSH_7', 'MSH.7', TS),                  # Date/Time Of Message
               ('MSH_8', 'MSH.8', str),                 # Security
               ('MSH_9', 'MSH.9', MSG),                 # Message Type
               ('MSH_10','MSH.10',str),                 # Message Control ID
               ('MSH_11','MSH.11',PT),                  # Processing ID
               ('MSH_12','MSH.12',VID, VID()),          # Version ID
               ('MSH_13','MSH.13',NM),                  # Sequence Number
               ('MSH_14','MSH.14',str),                 # Continuation Pointer
               ('MSH_15','MSH.15',ID),                  # Accept Acknowledgment Type
               ('MSH_16','MSH.16',ID),                  # Application Acknowledgment Type
               ('MSH_17','MSH.17',ID),                  # Country Code
               ('MSH_18','MSH.18',[str], 'UNICODE UTF-8'),# Character Set
               ('MSH_19','MSH.19',CE),                  # Principal Language Of Message
               ('MSH_20','MSH.20',ID),                  # Alternate Character Set Handling Scheme
               ('MSH_21','MSH.21',[EI]),                # Message Profile Identifier
             ]


class PID(THl7Compound):
    _items = [ ('PID_3', 'PID.3', [CX]),
               ('PID_5', 'PID.5', [XPN]),
               ('PID_7', 'PID.7', TS),
               ('PID_8', 'PID.8', str, 'U'),
             ]


class PV1(THl7Compound):
    _items = [ ('PV1_1', 'PV1.1', SI),      # Set ID - PV1
               ('PV1_2', 'PV1.2', IS),      # Patient Class {HL70004}
               ('PV1_3', 'PV1.3', PL),      # Assigned Patient Location
               ('PV1_4', 'PV1.4', IS),      # Admission Type {HL70007}
               ('PV1_5', 'PV1.5', CX),      # Preadmit Number
               ('PV1_6', 'PV1.6', PL),      # Prior Patient Location
               ('PV1_7', 'PV1.7', [XCN]),   # Attending Doctor {HL70010}
               ('PV1_8', 'PV1.8', [XCN]),   # Referring Doctor {HL70010}
               ('PV1_9', 'PV1.9', [XCN]),   # Consulting Doctor {HL70010}
               ('PV1_10', 'PV1.10', IS),    # Hospital Service {HL70069}
               ('PV1_11', 'PV1.11', PL),    # Temporary Location
               ('PV1_12', 'PV1.12', IS),    # Preadmit Test Indicator {HL70087}
               ('PV1_13', 'PV1.13', IS),    # Re-admission Indicator {HL70092}
               ('PV1_14', 'PV1.14', IS),    # Admit Source {HL70023}
               ('PV1_15', 'PV1.15', [IS]),  # Ambulatory Status {HL70009}
               ('PV1_16', 'PV1.16', IS),    # VIP Indicator {HL70099}
               ('PV1_17', 'PV1.17', [XCN]), # Admitting Doctor {HL70010}
               ('PV1_18', 'PV1.18', IS),    # Patient Type {HL70018}
               ('PV1_19', 'PV1.19', CX),    # Visit Number
               ('PV1_20', 'PV1.20', [FC]),  # Financial Class {HL70064}
               ('PV1_21', 'PV1.21', IS),    # Charge Price Indicator {HL70032}
               ('PV1_22', 'PV1.22', IS),    # Courtesy Code {HL70045}
               ('PV1_23', 'PV1.23', IS),    # Credit Rating {HL70046}
               ('PV1_24', 'PV1.24', [IS]),  # Contract Code {HL70044}
               ('PV1_25', 'PV1.25', [DT]),  # Contract Effective Date
               ('PV1_26', 'PV1.26', [NM]),  # Contract Amount
               ('PV1_27', 'PV1.27', [NM]),  # Contract Period
               ('PV1_28', 'PV1.28', IS),    # Interest Code {HL70073}
               ('PV1_29', 'PV1.29', IS),    # Transfer to Bad Debt Code {HL70110}
               ('PV1_30', 'PV1.30', DT),    # Transfer to Bad Debt Date
               ('PV1_31', 'PV1.31', IS),    # Bad Debt Agency Code {HL70021}
               ('PV1_32', 'PV1.32', NM),    # Bad Debt Transfer Amount
               ('PV1_33', 'PV1.33', NM),    # Bad Debt Recovery Amount
               ('PV1_34', 'PV1.34', IS),    # Delete Account Indicator {HL70111}
               ('PV1_35', 'PV1.35', DT),    # Delete Account Date
               ('PV1_36', 'PV1.36', IS),    # Discharge Disposition {HL70112}
               ('PV1_37', 'PV1.37', DLD),   # Discharged to Location {HL70113}
               ('PV1_38', 'PV1.38', CE),    # Diet Type {HL70114}
               ('PV1_39', 'PV1.39', IS),    # Servicing Facility {HL70115}
               ('PV1_40', 'PV1.40', IS),    # Bed Status {HL70116}
               ('PV1_41', 'PV1.41', IS),    # Account Status {HL70117}
               ('PV1_42', 'PV1.42', PL),    # Pending Location
               ('PV1_43', 'PV1.43', PL),    # Prior Temporary Location
               ('PV1_44', 'PV1.44', TS),    # Admit Date/Time
               ('PV1_45', 'PV1.45', [TS]),  # Discharge Date/Time
               ('PV1_46', 'PV1.46', NM),    # Current Patient Balance
               ('PV1_47', 'PV1.47', NM),    # Total Charges
               ('PV1_48', 'PV1.48', NM),    # Total Adjustments
               ('PV1_49', 'PV1.49', NM),    # Total Payments
               ('PV1_50', 'PV1.50', CX),    # Alternate Visit ID {HL70203}
               ('PV1_51', 'PV1.51', IS),    # Visit Indicator {HL70326}
               ('PV1_52', 'PV1.52', [XCN]), # Other Healthcare Provider {HL70010}
             ]



class PV2(THl7Compound):
    _items = [ ('PV2_1', 'PV2.1', PL),      # Prior Pending Location
               ('PV2_2', 'PV2.2', CE),      # Accommodation Code {HL70129}
               ('PV2_3', 'PV2.3', CE),      # Admit Reason
               ('PV2_4', 'PV2.4', CE),      # Transfer Reason
               ('PV2_5', 'PV2.5', [ST]),    # Patient Valuables
               ('PV2_6', 'PV2.6', ST),      # Patient Valuables Location
               ('PV2_7', 'PV2.7', [IS]),    # Visit User Code {HL70130}
               ('PV2_8', 'PV2.8', TS),      # Expected Admit Date/Time
               ('PV2_9', 'PV2.9', TS),      # Expected Discharge Date/Time
               ('PV2_10', 'PV2.10', NM),    # Estimated Length of Inpatient Stay
               ('PV2_11', 'PV2.11', NM),    # Actual Length of Inpatient Stay
               ('PV2_12', 'PV2.12', ST),    # Visit Description
               ('PV2_13', 'PV2.13', [XCN]), # Referral Source Code
               ('PV2_14', 'PV2.14', DT),    # Previous Service Date
               ('PV2_15', 'PV2.15', ID),    # Employment Illness Related Indicator {HL70136}
               ('PV2_16', 'PV2.16', IS),    # Purge Status Code {HL70213}
               ('PV2_17', 'PV2.17', DT),    # Purge Status Date
               ('PV2_18', 'PV2.18', IS),    # Special Program Code {HL70214}
               ('PV2_19', 'PV2.19', ID),    # Retention Indicator {HL70136}
               ('PV2_20', 'PV2.20', NM),    # Expected Number of Insurance Plans
               ('PV2_21', 'PV2.21', IS),    # Visit Publicity Code {HL70215}
               ('PV2_22', 'PV2.22', ID),    # Visit Protection Indicator {HL70136}
               ('PV2_23', 'PV2.23', [XON]), # Clinic Organization Name
               ('PV2_24', 'PV2.24', IS),    # Patient Status Code {HL70216}
               ('PV2_25', 'PV2.25', IS),    # Visit Priority Code {HL70217}
               ('PV2_26', 'PV2.26', DT),    # Previous Treatment Date
               ('PV2_27', 'PV2.27', IS),    # Expected Discharge Disposition {HL70112}
               ('PV2_28', 'PV2.28', DT),    # Signature on File Date
               ('PV2_29', 'PV2.29', DT),    # First Similar Illness Date
               ('PV2_30', 'PV2.30', CE),    # Patient Charge Adjustment Code {HL70218}
               ('PV2_31', 'PV2.31', IS),    # Recurring Service Code {HL70219}
               ('PV2_32', 'PV2.32', ID),    # Billing Media Code {HL70136}
               ('PV2_33', 'PV2.33', TS),    # Expected Surgery Date and Time
               ('PV2_34', 'PV2.34', ID),    # Military Partnership Code {HL70136}
               ('PV2_35', 'PV2.35', ID),    # Military Non-Availability Code {HL70136}
               ('PV2_36', 'PV2.36', ID),    # Newborn Baby Indicator {HL70136}
               ('PV2_37', 'PV2.37', ID),    # Baby Detained Indicator {HL70136}
               ('PV2_38', 'PV2.38', CE),    # Mode of Arrival Code {HL70430}
               ('PV2_39', 'PV2.39', [CE]),  # Recreational Drug Use Code {HL70431}
               ('PV2_40', 'PV2.40', CE),    # Admission Level of Care Code {HL70432}
               ('PV2_41', 'PV2.41', [CE]),  # Precaution Code {HL70433}
               ('PV2_42', 'PV2.42', CE),    # Patient Condition Code {HL70434}
               ('PV2_43', 'PV2.43', IS),    # Living Will Code {HL70315}
               ('PV2_44', 'PV2.44', IS),    # Organ Donor Code {HL70316}
               ('PV2_45', 'PV2.45', [CE]),  # Advance Directive Code {HL70435}
               ('PV2_46', 'PV2.46', DT),    # Patient Status Effective Date
               ('PV2_47', 'PV2.47', TS),    # Expected LOA Return Date/Time
               ('PV2_48', 'PV2.48', TS),    # Expected Pre-admission Testing Date/Time
               ('PV2_49', 'PV2.49', []),    # Notify Clergy Code {HL70534}
             ]


class ODT(THl7Compound):
    _items = [ ('ODT_1', 'ODT.1', CE),      # Tray Type {HL70160}
               ('ODT_2', 'ODT.2', [CE]),    # Service Period
               ('ODT_2', 'ODT.2', ST),      # Text Instruction
             ]



class ORC(THl7Compound):
    _items = [ ('ORC_1', 'ORC.1', ID),      # Order Control {HL70119}
               ('ORC_2', 'ORC.2', EI),      # Placer Order Number
               ('ORC_3', 'ORC.3', EI),      # Filler Order Number
               ('ORC_4', 'ORC.4', EI),      # Placer Group Number
               ('ORC_5', 'ORC.5', ID),      # Order Status {HL70038}
               ('ORC_6', 'ORC.6', ID),      # Response Flag {HL70121}
               ('ORC_7', 'ORC.7', [TS]),    # Quantity/Timing
               ('ORC_8', 'ORC.8', EIP),     # Parent
               ('ORC_9', 'ORC.9', TS),      # Date/Time of Transaction
               ('ORC_10', 'ORC.10', [XCN]), # Entered By
               ('ORC_11', 'ORC.11', [XCN]), # Verified By
               ('ORC_12', 'ORC.12', [XCN]), # Ordering Provider
               ('ORC_13', 'ORC.13', PL),    # Enterer's Location
               ('ORC_14', 'ORC.14', [XTN]), # Call Back Phone Number
               ('ORC_15', 'ORC.15', TS),    # Order Effective Date/Time
               ('ORC_16', 'ORC.16', CE),    # Order Control Code Reason
               ('ORC_17', 'ORC.17', CE),    # Entering Organization
               ('ORC_18', 'ORC.18', CE),    # Entering Device
               ('ORC_19', 'ORC.19', [XCN]), # Action By
               ('ORC_20', 'ORC.20', CE),    # Advanced Beneficiary Notice Code {HL70339}
               ('ORC_21', 'ORC.21', [XON]), # Ordering Facility Name
               ('ORC_22', 'ORC.22', [XAD]), # Ordering Facility Address
               ('ORC_23', 'ORC.23', [XTN]), # Ordering Facility Phone Number
               ('ORC_24', 'ORC.24', [XAD]), # Ordering Provider Address
               ('ORC_25', 'ORC.25', CWE),   # Order Status Modifier
               ('ORC_26', 'ORC.26', CWE),   # Advanced Beneficiary Notice Override Reason {HL70552}
               ('ORC_27', 'ORC.27', TS),    # Filler's Expected Availability Date/Time
               ('ORC_28', 'ORC.28', CWE),   # Confidentiality Code {HL70177}
               ('ORC_29', 'ORC.29', CWE),   # Order Type {HL70482}
               ('ORC_30', 'ORC.30', CNE),   # Enterer Authorization Mode {HL70483}
             ]


class OBR(THl7Compound):
    _items = [ ('OBR_1', 'OBR.1', SI),      # Set ID - OBR
               ('OBR_2', 'OBR.2', EI),      # Placer Order Number
               ('OBR_3', 'OBR.3', EI),      # Filler Order Number
               ('OBR_4', 'OBR.4', CE),      # Universal Service Identifier
               ('OBR_5', 'OBR.5', ID),      # Priority _ OBR
               ('OBR_6', 'OBR.6', TS),      # Requested Date/Time
               ('OBR_7', 'OBR.7', TS),      # Observation Date/Time
               ('OBR_8', 'OBR.8', TS),      # Observation End Date/Time
               ('OBR_9', 'OBR.9', CQ),      # Collection Volume
               ('OBR_10', 'OBR.10', [XCN]), # Collector Identifier
               ('OBR_11', 'OBR.11', ID),    # Specimen Action Code {HL70065}
               ('OBR_12', 'OBR.12', CE),    # Danger Code
               ('OBR_13', 'OBR.13', ST),    # Relevant Clinical Information
               ('OBR_14', 'OBR.14', TS),    # Specimen Received Date/Time
               ('OBR_15', 'OBR.15', SPS),   # Specimen Source
               ('OBR_16', 'OBR.16', [XCN]), # Ordering Provider
               ('OBR_17', 'OBR.17', [XTN]), # Order Callback Phone Number
               ('OBR_18', 'OBR.18', ST),    # Placer Field 1
               ('OBR_19', 'OBR.19', ST),    # Placer Field 2
               ('OBR_20', 'OBR.20', ST),    # Filler Field 1
               ('OBR_21', 'OBR.21', ST),    # Filler Field 2
               ('OBR_22', 'OBR.22', TS),    # Results Rpt/Status Chng - Date/Time
               ('OBR_23', 'OBR.23', MOC),   # Charge to Practice
               ('OBR_24', 'OBR.24', ID),    # Diagnostic Serv Sect ID {HL70074}
               ('OBR_25', 'OBR.25', ID),    # Result Status {HL70123}
               ('OBR_26', 'OBR.26', PRL),   # Parent Result
               ('OBR_27', 'OBR.27', [TQ]),  # Quantity/Timing
               ('OBR_28', 'OBR.28', [XCN]), # Result Copies To
               ('OBR_29', 'OBR.29', EIP),   # Parent
               ('OBR_30', 'OBR.30', ID),    # Transportation Mode {HL70124}
               ('OBR_31', 'OBR.31', [CE]),  # Reason for Study
               ('OBR_32', 'OBR.32', NDL),   # Principal Result Interpreter
               ('OBR_33', 'OBR.33', [NDL]), # Assistant Result Interpreter
               ('OBR_34', 'OBR.34', [NDL]), # Technician
               ('OBR_35', 'OBR.35', [NDL]), # Transcriptionist
               ('OBR_36', 'OBR.36', TS),    # Scheduled Date/Time
               ('OBR_37', 'OBR.37', NM),    # Number of Sample Containers *
               ('OBR_38', 'OBR.38', [CE]),  # Transport Logistics of Collected Sample
               ('OBR_39', 'OBR.39', [CE]),  # Collector's Comment *
               ('OBR_40', 'OBR.40', CE),    # Transport Arrangement Responsibility
               ('OBR_41', 'OBR.41', ID),    # Transport Arranged {HL70224}
               ('OBR_42', 'OBR.42', ID),    # Escort Required {HL70225}
               ('OBR_43', 'OBR.43', [CE]),  # Planned Patient Transport Comment
               ('OBR_44', 'OBR.44', CE),    # Procedure Code {HL70088}
               ('OBR_45', 'OBR.45', [CE]),  # Procedure Code Modifier {HL70340}
               ('OBR_46', 'OBR.46', [CE]),  # Placer Supplemental Service Information {HL70411}
               ('OBR_47', 'OBR.47', [CE]),  # Filler Supplemental Service Information {HL70411}
               ('OBR_48', 'OBR.48', CWE),   # Medically Necessary Duplicate Procedure Reason. {HL70476}
               ('OBR_49', 'OBR.49', IS),    # Result Handling {HL70507}
             ]


class MSA(THl7Compound):
    _items = [ ('MSA_1', 'MSA.1', str, 'AA'),
               ('MSA_2', 'MSA.2', str),
               ('MSA_3', 'MSA.3', str),
             ]


class ERR(THl7Compound):
    _items = [ ('ERR_1', 'ERR.1', [ELD]),       # Error Code and Location
               ('ERR_2', 'ERR.2', [ERL]),       # Error Location
               ('ERR_3', 'ERR.3', CWE),         # HL7 Error Code
               ('ERR_4', 'ERR.4', ID),          # Severity
               ('ERR_5', 'ERR.5', CWE),         # Application Error Code
               ('ERR_6', 'ERR.6', [str]),       # Application Error Parameter
               ('ERR_7', 'ERR.7', TX),          # Diagnostic Information
               ('ERR_8', 'ERR.8', TX),          # User Message
               ('ERR_9', 'ERR.9', [IS]),        # Inform Person Indicator
               ('ERR_10', 'ERR.10', CWE),       # Override Type
               ('ERR_11', 'ERR.11', [CWE]),     # Override Reason Code
               ('ERR_12', 'ERR.12', [XTN]),     # Help Desk Contact Point
             ]


class NK1(THl7Compound):
    _items = [ ('NK1_1', 'NK1.1', SI),          # Set ID - NK1
               ('NK1_2', 'NK1.2', [XPN]),       # Name
               ('NK1_3', 'NK1.3', CE),          # Relationship {HL70063}
               ('NK1_4', 'NK1.4', [XAD]),       # Address
               ('NK1_5', 'NK1.5', [XTN]),       # Phone Number
               ('NK1_6', 'NK1.6', [XTN]),       # Business Phone Number
               ('NK1_7', 'NK1.7', CE),          # Contact Role {HL70131}
               ('NK1_8', 'NK1.8', DT),          # Start Date
               ('NK1_9', 'NK1.9', DT),          # End Date
               ('NK1_10', 'NK1.10', ST),        # Next of Kin / Associated Parties Job Title
               ('NK1_11', 'NK1.11', JCC),       # Next of Kin / Associated Parties Job Code/Class
               ('NK1_12', 'NK1.12', CX),        # Next of Kin / Associated Parties Employee Number
               ('NK1_13', 'NK1.13', [XON]),     # Organization Name - NK1
               ('NK1_14', 'NK1.14', CE),        # Marital Status {HL70002}
               ('NK1_15', 'NK1.15', IS),        # Administrative Sex {HL70001}
               ('NK1_16', 'NK1.16', TS),        # Date/Time of Birth
               ('NK1_17', 'NK1.17', [IS]),      # Living Dependency {HL70223}
               ('NK1_18', 'NK1.18', [IS]),      # Ambulatory Status {HL70009}
               ('NK1_19', 'NK1.19', [CE]),      # Citizenship {HL70171}

               ('NK1_20', 'NK1.20', CE),        # Primary Language {HL70296}
               ('NK1_21', 'NK1.21', IS),        # Living Arrangement {HL70220}
               ('NK1_22', 'NK1.22', CE),        # Publicity Code {HL70215}
               ('NK1_23', 'NK1.23', ID),        # Protection Indicator {HL70136}
               ('NK1_24', 'NK1.24', IS),        # Student Indicator {HL70231}
               ('NK1_25', 'NK1.25', CE),        # Religion {HL70006}
               ('NK1_26', 'NK1.26', [XPN]),     # Mother's Maiden Name
               ('NK1_27', 'NK1.27', CE),        # Nationality {HL70212}
               ('NK1_28', 'NK1.28', [CE]),      # Ethnic Group {HL70189}
               ('NK1_29', 'NK1.29', [CE]),      # Contact Reason {HL70222}
               ('NK1_30', 'NK1.30', [XPN]),     # Contact Person's Name
               ('NK1_31', 'NK1.31', [XTN]),     # Contact Person's Telephone Number
               ('NK1_32', 'NK1.32', [XAD]),     # Contact Person's Address
               ('NK1_33', 'NK1.33', [CX]),      # Next of Kin/Associated Party's Identifiers
               ('NK1_34', 'NK1.34', IS),        # Job Status {HL70311}
               ('NK1_35', 'NK1.35', [CE]),      # Race {HL70005}
               ('NK1_36', 'NK1.36', IS),        # Handicap {HL70295}
               ('NK1_37', 'NK1.37', ST),        # Contact Person Social Security Number
               ('NK1_38', 'NK1.38', ST),        # Next of Kin Birth Place
               ('NK1_39', 'NK1.39', IS),        # VIP Indicator {HL70099}
             ]


class NTE(THl7Compound):
    _items = [ ('NTE_1', 'NTE.1', str),         # Set ID - NTE
               ('NTE_2', 'NTE.2', ID),          # Source of Comment
               ('NTE_3', 'NTE.3', [FT]),        # Comment
               ('NTE_4', 'NTE.4', CE),          # Comment Type
             ]


class OBX(THl7Compound):
    _items = [ ('OBX_1', 'OBX.1', SI),          # Set ID - OBX
               ('OBX_2', 'OBX.2', ID),          # Value Type {HL70125}
               ('OBX_3', 'OBX.3', CE),          # Observation Identifier
               ('OBX_4', 'OBX.4', ST),          # Observation Sub-ID
               ('OBX_5', 'OBX.5', [var]),       # Observation Value
               ('OBX_6', 'OBX.6', CE),          # Units
               ('OBX_7', 'OBX.7', ST),          # References Range
               ('OBX_8', 'OBX.8', [IS]),        # Abnormal Flags {HL70078}
               ('OBX_9', 'OBX.9', NM),          # Probability
               ('OBX_10', 'OBX.10', [ID]),      # Nature of Abnormal Test {HL70080}
               ('OBX_11', 'OBX.11', ID),        # Observation Result Status {HL70085}
               ('OBX_12', 'OBX.12', TS),        # Effective Date of Reference Range
               ('OBX_13', 'OBX.13', ST),        # User Defined Access Checks
               ('OBX_14', 'OBX.14', TS),        # Date/Time of the Observation
               ('OBX_15', 'OBX.15', CE),        # Producer's ID
               ('OBX_16', 'OBX.16', [XCN]),     # Responsible Observer
               ('OBX_17', 'OBX.17', [CE]),      # Observation Method
               ('OBX_18', 'OBX.18', [EI]),      # Equipment Instance Identifier
               ('OBX_19', 'OBX.19', TS),        # Date/Time of the Analysis
             ]


class PD1(THl7Compound):
    _items = [ ('PD1_1', 'PD1.1', [IS]),        # Living Dependency {HL70223}
               ('PD1_2', 'PD1.2', IS),          # Living Arrangement {HL70220}
               ('PD1_3', 'PD1.3', [XON]),       # Patient Primary Facility
               ('PD1_4', 'PD1.4', [XCN]),       # Patient Primary Care Provider Name &amp; ID No.
               ('PD1_5', 'PD1.5', IS),          # Student Indicator {HL70231}
               ('PD1_6', 'PD1.6', IS),          # Handicap {HL70295}
               ('PD1_7', 'PD1.7', IS),          # Living Will Code {HL70315}
               ('PD1_8', 'PD1.8', IS),          # Organ Donor Code {HL70316}
               ('PD1_9', 'PD1.9', ID),          # Separate Bill {HL70136}
               ('PD1_10', 'PD1.10', [CX]),      # Duplicate Patient
               ('PD1_11', 'PD1.11', CE),        # Publicity Code {HL70215}
               ('PD1_12', 'PD1.12', ID),        # Protection Indicator {HL70136}
               ('PD1_13', 'PD1.13', DT),        # Protection Indicator Effective Date
               ('PD1_14', 'PD1.14', [XON]),     # Place of Worship
               ('PD1_15', 'PD1.15', [CE]),      # Advance Directive Code {HL70435}
               ('PD1_16', 'PD1.16', IS),        # Immunization Registry Status {HL70441}
               ('PD1_17', 'PD1.17', DT),        # Immunization Registry Status Effective Date
               ('PD1_18', 'PD1.18', DT),        # Publicity Code Effective Date
               ('PD1_19', 'PD1.19', IS),        # Military Branch {HL70140}
               ('PD1_20', 'PD1.20', IS),        # Military Rank/Grade {HL70141}
               ('PD1_21', 'PD1.21', IS),        # Military Status {HL70142}
             ]


class RQ1(THl7Compound):
    _items = [ ('RQ1_1', 'RQ1.1', str),         # Anticipated Price
               ('RQ1_2', 'RQ1.2', CE),          # Manufacturer Identifier
               ('RQ1_3', 'RQ1.3', str),         # Manufacturer's Catalog
               ('RQ1_4', 'RQ1.4', CE),          # Vendor ID
               ('RQ1_5', 'RQ1.5', str),         # Vendor Catalog
               ('RQ1_6', 'RQ1.6', ID),          # Taxable
               ('RQ1_7', 'RQ1.7', ID),          # Substitute Allowed
             ]


class RQD(THl7Compound):
    _items = [ ('RQD_1', 'RQD.1', SI),          # Requisition Line Number
               ('RQD_2', 'RQD.2', CE),          # Item Code - Internal
               ('RQD_3', 'RQD.3', CE),          # Item Code - External
               ('RQD_4', 'RQD.4', CE),          # Hospital Item Code
               ('RQD_5', 'RQD.5', NM),          # Requisition Quantity
               ('RQD_6', 'RQD.6', CE),          # Requisition Unit of Measure
               ('RQD_7', 'RQD.7', IS),          # Dept. Cost Center
               ('RQD_8', 'RQD.8', IS),          # Item Natural Account Code
               ('RQD_9', 'RQD.9', CE),          # Deliver To ID
               ('RQD_10', 'RQD.10', DT),        # Date Needed
             ]


class RXO(THl7Compound):
    _items = [ ('RXO_1', 'RXO.1', CE),          # Requested Give Code
               ('RXO_2', 'RXO.2', NM),          # Requested Give Amount - Minimum
               ('RXO_3', 'RXO.3', NM),          # Requested Give Amount - Maximum
               ('RXO_4', 'RXO.4', CE),          # Requested Give Units
               ('RXO_5', 'RXO.5', CE),          # Requested Dosage Form
               ('RXO_6', 'RXO.6', [CE]),        # Provider's Pharmacy/Treatment Instructions
               ('RXO_7', 'RXO.7', [CE]),        # Provider's Administration Instructions
               ('RXO_8', 'RXO.8', LA1),         # Deliver-To Location
               ('RXO_9', 'RXO.9', ID),          # Allow Substitutions
               ('RXO_10', 'RXO.10', CE),        # Requested Dispense Code
               ('RXO_11', 'RXO.11', NM),        # Requested Dispense Amount
               ('RXO_12', 'RXO.12', CE),        # Requested Dispense Units
               ('RXO_13', 'RXO.13', NM),        # Number Of Refills
               ('RXO_14', 'RXO.14', [XCN]),     # Ordering Provider's DEA Number
               ('RXO_15', 'RXO.15', [XCN]),     # Pharmacist/Treatment Supplier's Verifier ID
               ('RXO_16', 'RXO.16', ID),        # Needs Human Review
               ('RXO_17', 'RXO.17', str),       # Requested Give Per (Time Unit)
               ('RXO_18', 'RXO.18', NM),        # Requested Give Strength
               ('RXO_19', 'RXO.19', CE),        # Requested Give Strength Units
               ('RXO_20', 'RXO.20', [CE]),      # Indication
               ('RXO_21', 'RXO.21', str),       # Requested Give Rate Amount
               ('RXO_22', 'RXO.22', CE),        # Requested Give Rate Units
               ('RXO_23', 'RXO.23', CQ),        # Total Daily Dose
               ('RXO_24', 'RXO.24', [CE]),      # Supplementary Code
               ('RXO_25', 'RXO.25', NM),        # Requested Drug Strength Volume
               ('RXO_26', 'RXO.26', CWE),       # Requested Drug Strength Volume Units
               ('RXO_27', 'RXO.27', ID),        # Pharmacy Order Type
               ('RXO_28', 'RXO.28', NM),        # Dispensing Interval
             ]


class SFT(THl7Compound):
    _items = [ ('SFT_1', 'SFT.1', XON),         # Software Vendor Organization
               ('SFT_2', 'SFT.2', str),         # Software Certified Version or Release Number
               ('SFT_3', 'SFT.3', str),         # Software Product Name
               ('SFT_4', 'SFT.4', str),         # Software Binary ID
               ('SFT_5', 'SFT.5', TX),          # Software Product Information
               ('SFT_6', 'SFT.6', TS),          # Software Install Date
             ]

class SPM(THl7Compound):
    _items = [ ('SPM_1', 'SPM.1', SI),         # Set ID _ SPM
               ('SPM_2', 'SPM.2', EIP),        # Specimen ID
               ('SPM_3', 'SPM.3', [EIP]),      # Specimen Parent IDs
               ('SPM_4', 'SPM.4', CWE),        # Specimen Type {HL70487}
               ('SPM_5', 'SPM.5', [CWE]),      # Specimen Type Modifier
               ('SPM_6', 'SPM.6', [CWE]),      # Specimen Additives {HL70371}
               ('SPM_7', 'SPM.7', CWE),        # Specimen Collection Method {HL70488}
               ('SPM_8', 'SPM.8', CWE),        # Specimen Source Site
               ('SPM_9', 'SPM.9', [CWE]),      # Specimen Source Site Modifier {HL70542}
               ('SPM_10', 'SPM.10', CWE),      # Specimen Collection Site {HL70543}
               ('SPM_11', 'SPM.11', [CWE]),    # Specimen Role {HL70369}
               ('SPM_12', 'SPM.12', CQ),       # Specimen Collection Amount
               ('SPM_13', 'SPM.13', NM),       # Grouped Specimen Count
               ('SPM_14', 'SPM.14', [ST]),     # Specimen Description
               ('SPM_15', 'SPM.15', [CWE]),    # Specimen Handling Code {HL70376}
               ('SPM_16', 'SPM.16', [CWE]),    # Specimen Risk Code
               ('SPM_17', 'SPM.17', DR),       # Specimen Collection Date/Time
               ('SPM_18', 'SPM.18', TS),       # Specimen Received Date/Time
               ('SPM_19', 'SPM.19', TS),       # Specimen Expiration Date/Time
               ('SPM_20', 'SPM.20', ID),       # Specimen Availability {HL70136}
               ('SPM_21', 'SPM.21', [CWE]),    # Specimen Reject Reason {HL70490}
               ('SPM_22', 'SPM.22', CWE),      # Specimen Quality {HL70491}
               ('SPM_23', 'SPM.23', CWE),      # Specimen Appropriateness {HL70492}
               ('SPM_24', 'SPM.24', [CWE]),    # Specimen Condition {HL70493}
               ('SPM_25', 'SPM.25', CQ),       # Specimen Current Quantity
               ('SPM_26', 'SPM.26', NM),       # Number of Specimen Containers
               ('SPM_27', 'SPM.27', CWE),      # Container Type
               ('SPM_28', 'SPM.28', CWE),      # Container Condition {HL70544}
               ('SPM_29', 'SPM.29', CWE),       # Specimen Child Role {HL70494}
             ]


class TQ1(THl7Compound):
    _items = [ ('TQ1_1', 'TQ1.1', SI),          # Set ID - TQ1
               ('TQ1_2', 'TQ1.2', CQ),          # Quantity
               ('TQ1_3', 'TQ1.3', [RPT]),       # Repeat Pattern {HL70335}
               ('TQ1_4', 'TQ1.4', [TM]),        # Explicit Time
               ('TQ1_5', 'TQ1.5', [CQ]),        # Relative Time and Units
               ('TQ1_6', 'TQ1.6', CQ),          # Service Duration
               ('TQ1_7', 'TQ1.7', TS),          # Start date/time
               ('TQ1_8', 'TQ1.8', TS),          # End date/time
               ('TQ1_9', 'TQ1.9', [CWE]),       # Priority {HL70485}
               ('TQ1_10', 'TQ1.10', TX),        # Condition text
               ('TQ1_11', 'TQ1.11', TX),        # Text instruction
               ('TQ1_12', 'TQ1.12', ID),        # Conjunction {HL70427}
               ('TQ1_13', 'TQ1.13', CQ),        # Occurrence duration
               ('TQ1_14', 'TQ1.14', NM),        # Total occurrence's
             ]


class TQ2(THl7Compound):
    _items = [ ('TQ2_1', 'TQ2.1', SI),          # Set ID - TQ2
               ('TQ2_2', 'TQ2.2', ID),          # Sequence/Results Flag {HL70503}
               ('TQ2_3', 'TQ2.3', [EI]),        # Related Placer Number
               ('TQ2_4', 'TQ2.4', [EI]),        # Related Filler Number
               ('TQ2_5', 'TQ2.5', [EI]),        # Related Placer Group Number
               ('TQ2_6', 'TQ2.6', ID),          # Sequence Condition Code {HL70504}
               ('TQ2_7', 'TQ2.7', ID),          # Cyclic Entry/Exit Indicator {HL70505}
               ('TQ2_8', 'TQ2.8', CQ),          # Sequence Condition Time Interval
               ('TQ2_9', 'TQ2.9', NM),          # Cyclic Group Maximum Number of Repeats
               ('TQ2_10', 'TQ2.10', ID),        # Special Service Request Relationship {HL70506}
             ]

