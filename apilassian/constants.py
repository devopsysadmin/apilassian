# JIRA CONSTANTS

# Jira API URL
JIRA_API_PATH = '/rest/api/2'

# Jira issue regex
JIRA_ISSUE_REGEX = r'.*(?P<issue>DB-\d+).*'

# Jira issue types
JIRA_TYPE_DEFECT = 'Defect'
JIRA_TYPE_FEATURE = 'Feature'
JIRA_TYPE_STORY = 'Story'

# Jira issue statuses
JIRA_STATUS_NEW = 'New'
JIRA_STATUS_ANALYSING = 'Analysing'
JIRA_STATUS_READY = 'Ready'
JIRA_STATUS_INPROGRESS = 'In Progress'
JIRA_STATUS_BLOCKED = 'Blocked'
JIRA_STATUS_CLOSED = 'Closed'
JIRA_STATUS_2REWORK = 'To Rework'
JIRA_STATUS_R2VERIFY = 'Ready To Verify'
JIRA_STATUS_R4RELEASE = 'Ready for release'
JIRA_STATUS_RELEASED = 'Released'
JIRA_STATUS_DISCARDED = 'Discarded'
JIRA_STATUS_ACCEPTED = 'Accepted'
JIRA_STATUS_REOPEN = 'Reopen'

# Jira transition type
TRANSITION_TYPE_MANUAL = 'manual'
TRANSITION_TYPE_AUTO = 'auto'

# Jira issue transition ids, depending on:
#  - destination status
JIRA_COMMON_TRANSITION_IDS = {
    JIRA_STATUS_ANALYSING: 11,
    JIRA_STATUS_READY: 21,
    JIRA_STATUS_INPROGRESS: 31,
    JIRA_STATUS_R2VERIFY: 41,
    JIRA_STATUS_DISCARDED: 51,
    JIRA_STATUS_ACCEPTED: 61,
    JIRA_STATUS_BLOCKED: 71,
    JIRA_STATUS_2REWORK: 81,
    JIRA_STATUS_NEW: 91,
    JIRA_STATUS_R4RELEASE: 101,
    JIRA_STATUS_RELEASED: 111
}

# Jira issue transition ids, depending on:
#  - destination status
#  - issue type
#  - auto/manual transition type
# extends common transition ids doing:
#    common.update(specific[issue_type][transition_type])
JIRA_SPECIFIC_TRANSITION_IDS = {
    JIRA_TYPE_DEFECT: {
        TRANSITION_TYPE_MANUAL: {
            JIRA_STATUS_CLOSED: 121,
            JIRA_STATUS_REOPEN: 131
        },
        TRANSITION_TYPE_AUTO: {
            JIRA_STATUS_CLOSED: 121,
            JIRA_STATUS_REOPEN: 131,
            JIRA_STATUS_RELEASED: 141
        }
    },
    JIRA_TYPE_STORY: {
        TRANSITION_TYPE_AUTO: {
            JIRA_STATUS_RELEASED: 121
        }
    },
    JIRA_TYPE_FEATURE: {
        TRANSITION_TYPE_AUTO: {
            JIRA_STATUS_RELEASED: 121
        }
    }
}

# BBUCKET CONSTANTS

# BBucket API URL
BBUCKET_API_PATH = '/rest/api/1.0'
BBUCKET_BUILD_API_PATH = '/rest/build-status/1.0'
BBUCKET_PERM_API_PATH = '/rest/branch-permissions/2.0'

# BBUCKET permissions
BBUCKET_PERM_READONLY = 'read-only'
BBUCKET_PERM_PULLREQUESTONLY = 'pull-request-only'
BBUCKET_PERM_FASTFORWARDONLY = 'fast-forward-only'
BBUCKET_PERM_NODELETES = 'no-deletes'

BBUCKET_MATCHERTYPE_BRANCH = 'BRANCH'
BBUCKET_MATCHERTYPE_PATTERN = 'PATTERN'
