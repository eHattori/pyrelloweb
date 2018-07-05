from django.db import migrations


class Migration(migrations.Migration):
    def delete_charts(apps, schema_editor):
        ChartLeadtime = apps.get_model("pyrellowebapp", "ChartLeadtime")
        ChartLeadtime.objects.all().delete()

    dependencies = [('pyrellowebapp', '0026_auto_20180622_1958'),]
    operations = [
        migrations.RunPython(delete_charts),
    ] 

