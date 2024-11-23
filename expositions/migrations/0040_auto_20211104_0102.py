from django.db import migrations


def convert_milestone_from_snippet_to_block(apps, schema_editor):
    """Convert Old Milestone Snippet to StreamField Content."""

    TimeLine = apps.get_model("expositions", "TimeLine")
    for time_line in TimeLine.objects.iterator():
        print(
            "\nConvirtiendo Hitos de Linea de Tiempo: ",
            time_line.title,
            " ID:",
            time_line.pk,
        )
        new_milestones = []
        for milestone in time_line.milestones.iterator():
            milestone_block = {
                "type": "time_line_milestone",
                "value": {
                    "title": milestone.title,
                    "short_description": milestone.short_description,
                    "long_description": milestone.long_description,
                    "publish_date": milestone.publish_date,
                    "image": milestone.image_id,
                    "start_date": milestone.start_date,
                    "start_date_title": milestone.start_date_title,
                    "start_place": milestone.start_place,
                    "subtitle_1": milestone.subtitle_1,
                    "subtitle_2": milestone.subtitle_2,
                    "end_date": milestone.end_date,
                    "end_date_title": milestone.end_date_title,
                    "end_place": milestone.end_place,
                    "category": milestone.category,
                    "is_avatar": milestone.is_avatar,
                    "resources": [],
                },
            }
            for resource in milestone.resources.iterator():
                milestone_block["value"]["resources"].append(
                    {
                        "resource": resource.resource_id,
                        "title": resource.title,
                        "description": resource.description,
                        "creator": resource.creator,
                        "date": resource.date,
                        "image": resource.image_id,
                        "type": resource.type_id,
                    }
                )

            new_milestones.append(milestone_block)
        time_line.milestones_content.stream_data = new_milestones
        time_line.save()


class Migration(migrations.Migration):

    dependencies = [
        ("expositions", "0039_auto_20211103_2143"),
    ]

    operations = [
        migrations.RunPython(
            convert_milestone_from_snippet_to_block,
            migrations.RunPython.noop,
        )
    ]
