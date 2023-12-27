/** @odoo-module */

import { registry } from '@web/core/registry';
import { CharField } from '@web/views/fields/char/char_field';
import { formatChar } from '@web/views/fields/formatters';

class TaskNameWithChildText extends CharField {
    get formattedSubtaskCount() {
        return formatChar(this.props.record.data.allow_subtasks && this.props.record.data.child_text || '');
    }
}

TaskNameWithChildText.template = 'project.TaskNameWithChildText';

registry.category('fields').add('name_subtask_count', TaskNameWithChildText);
