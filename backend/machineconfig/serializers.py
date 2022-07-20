#!/usr/bin/env python3

from rest_framework import serializers
from rest_flex_fields import FlexFieldsModelSerializer

from drf_writable_nested import WritableNestedModelSerializer
from drf_writable_nested import UniqueFieldsMixin

from machineconfig.models import Site
from machineconfig.models import Hostname
from machineconfig.models import PuppetMachine
from machineconfig.models import Webcam
from machineconfig.models import NetworkDevice
from machineconfig.models import NetworkInterface
from machineconfig.models import NetworkInterfaceConfiguration
from machineconfig.models import UnrecognizedPXEDevice
from machineconfig.models import BootHistory
from machineconfig.models import BuildHistory
from machineconfig.models import NTPServer

from contextlib import ContextDecorator
import validators
import re

class mycontext(ContextDecorator):
    def __init__(self, message):
        self.message = message

    def __enter__(self):
        print('ENTER:', self.message)
        return self

    def __exit__(self, *exc):
        print('EXIT:', self.message)
        return False

class DNSRecordSerializer(serializers.Serializer):
    '''Trivial serializer for manually generated field'''
    hostname = serializers.CharField(read_only=True)
    record_type = serializers.CharField(read_only=True)
    target = serializers.CharField(read_only=True)

    class Meta:
        model = None

class DHCPRecordSerializer(serializers.Serializer):
    '''Trivial serializer for manually generated field'''
    macaddress = serializers.CharField(read_only=True)
    ipaddress = serializers.CharField(read_only=True)
    hostname = serializers.CharField(read_only=True)

    class Meta:
        model = None

class BootHistorySerializer(FlexFieldsModelSerializer):
    class Meta:
        model = BootHistory
        exclude = (
            'id',
            'puppetmachine',
        )
        expandable_fields = {
            'puppetmachine': (
                'machineconfig.PuppetMachineSerializer',
                {
                    'many': False,
                    'read_only': True,
                    'required': False,
                    'allow_null': True,
                },
            ),
            'networkdevice': (
                'machineconfig.NetworkDeviceSerializer',
                {
                    'many': False,
                    'source': 'puppetmachine.networkdevice',
                    'read_only': True,
                    'required': False,
                    'allow_null': True,
                    'expand': [
                        'site',
                    ],
                },
            ),
        }

class BuildHistorySerializer(FlexFieldsModelSerializer):
    class Meta:
        model = BuildHistory
        exclude = (
            'id',
            'puppetmachine',
        )
        expandable_fields = {
            'puppetmachine': (
                'machineconfig.PuppetMachineSerializer',
                {
                    'many': False,
                    'read_only': True,
                    'required': False,
                    'allow_null': True,
                },
            ),
            'networkdevice': (
                'machineconfig.NetworkDeviceSerializer',
                {
                    'many': False,
                    'source': 'puppetmachine.networkdevice',
                    'read_only': True,
                    'required': False,
                    'allow_null': True,
                },
            ),
        }

class NTPServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = NTPServer
        exclude = (
            'id',
            'site',
            'created_at',
        )

# Serializers define the API representation.
class HostnameSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
    def validate_hostname(self, value):
        # check for the other standard hostname rules
        # http://stackoverflow.com/questions/2532053/validate-a-hostname-string
        allowed = re.compile(r'(?!-)[A-Z\d-]{1,63}(?<!-)$', re.IGNORECASE)
        if not all(allowed.match(x) for x in value.split('.')):
            raise serializers.ValidationError('Hostname contains invalid characters')

        return value.lower()

    class Meta:
        model = Hostname
        fields = (
            'id',
            'hostname',
        )

# Serializers define the API representation.
class NetworkInterfaceConfigurationSerializer(UniqueFieldsMixin, WritableNestedModelSerializer):
    ipaddress = serializers.IPAddressField(required=True, allow_null=True, allow_blank=True)
    hostname_set = HostnameSerializer(many=True, read_only=False)

    class Meta:
        model = NetworkInterfaceConfiguration
        fields = (
            'id',
            'ipaddress',
            'hostname_set',
        )

    @mycontext('NetworkInterfaceConfigurationSerializer::validate')
    def validate(self, data):
        print(f'NetworkInterfaceConfigurationSerializer::validate: {data}')
        return data

    @mycontext('NetworkInterfaceConfigurationSerializer::create')
    def create(self, validated_data):
        print(f'NetworkInterfaceConfigurationSerializer::create: CREATE')
        return super().create(validated_data=validated_data)

    @mycontext('NetworkInterfaceConfigurationSerializer::update')
    def update(self, instance, validated_data):
        print(f'NetworkInterfaceConfigurationSerializer::update: UPDATE')
        # Remove our child objects from the database before we update
        # We're within a transaction thanks to the ViewSet::perform_update call
        instance.hostname_set.all().delete()
        return super().update(instance=instance, validated_data=validated_data)

# Serializers define the API representation.
class NetworkInterfaceSerializer(UniqueFieldsMixin, WritableNestedModelSerializer):
    networkinterfaceconfiguration_set = NetworkInterfaceConfigurationSerializer(
        many=True,
        read_only=False,
    )

    @mycontext('NetworkInterfaceSerializer::validate')
    def validate(self, data):
        print(f'NetworkInterfaceSerializer::validate: {data}')
        return super().validate(data)

    def validate_mac(self, value):
        # convert to our canonical format
        value = value.lower()
        value = value.replace('-', ':')

        if not validators.mac_address(value):
            raise serializers.ValidationError('MAC Address is invalid')

        # Ethernet reserved address is not allowed
        if value == '00:00:00:00:00:00':
            raise serializers.ValidationError('MAC address must not be 00:00:00:00:00:00 (reserved)')

        # Ethernet broadcast address is not allowed
        if value == 'ff:ff:ff:ff:ff:ff':
            raise serializers.ValidationError('MAC address must not be ff:ff:ff:ff:ff:ff (broadcast)')

        return value

    class Meta:
        model = NetworkInterface
        fields = (
            'id',
            'mac',
            'description',
            'networkinterfaceconfiguration_set',
        )

    @mycontext('NetworkInterfaceSerializer::create')
    def create(self, validated_data):
        print(f'NetworkInterfaceSerializer::create: CREATE')
        return super().create(validated_data=validated_data)

    @mycontext('NetworkInterfaceSerializer::update')
    def update(self, instance, validated_data):
        print(f'NetworkInterfaceSerializer::update: UPDATE')
        return super().update(instance=instance, validated_data=validated_data)

class PuppetFactsSerializer(serializers.Serializer):
    name = serializers.ReadOnlyField()
    value = serializers.ReadOnlyField()

    class Meta:
        model = None

# Serializers define the API representation.
class WebcamSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Webcam
        fields = (
            'adminurl',
            'imageurl',
            'is_enabled',
            'is_public',
            'is_dome',
        )
        expandable_fields = {
        }

    @mycontext('WebcamSerializer::validate')
    def validate(self, data):
        print(f'WebcamSerializer::validate: {data}')
        return data

    @mycontext('WebcamSerializer::create')
    def create(self, validated_data):
        print(f'WebcamSerializer::create: CREATE')
        return super().create(validated_data=validated_data)

    @mycontext('WebcamSerializer::update')
    def update(self, instance, validated_data):
        print(f'WebcamSerializer::update: UPDATE')
        return super().update(instance=instance, validated_data=validated_data)

# Serializers define the API representation.
class PuppetMachineSerializer(FlexFieldsModelSerializer):
    # History API: Boot History
    lastboot_at = serializers.ReadOnlyField()
    boot_history = serializers.ListField(
        child=BootHistorySerializer(),
        read_only=True,
    )

    # History API: Build History
    lastbuild_at = serializers.ReadOnlyField()
    build_history = serializers.ListField(
        child=BuildHistorySerializer(),
        read_only=True,
    )

    class Meta:
        model = PuppetMachine
        fields = (
            #'facts',
            #'lcogtinstruments',
            'operatingsystem',
            'partitionscheme',
            'partitionscheme_custom',
            'boot_mode',
            'lastboot_at',
            'boot_history',
            'lastbuild_at',
            'build_history',
        )
        expandable_fields = {
            'facts': (
                PuppetFactsSerializer,
                {
                    'many': True,
                    'read_only': True,
                },
            ),
            'lcogtinstruments': (
                serializers.ListField,
                {
                    'source': 'lcogtinstruments',
                    'child': serializers.CharField(read_only=True),
                    'read_only': True,
                },
            ),
        }

    @mycontext('PuppetMachineSerializer::validate')
    def validate(self, data):
        print(f'PuppetMachineSerializer::validate: {data}')
        return data

    @mycontext('PuppetMachineSerializer::create')
    def create(self, validated_data):
        print(f'PuppetMachineSerializer::create: CREATE')
        return super().create(validated_data=validated_data)

    @mycontext('PuppetMachineSerializer::update')
    def update(self, instance, validated_data):
        print(f'PuppetMachineSerializer::update: UPDATE')
        return super().update(instance=instance, validated_data=validated_data)

# https://stackoverflow.com/a/53944566
class Base64ImageField(serializers.ImageField):
    '''
    A Django REST framework field for handling image-uploads through raw post data.
    It uses base64 for encoding and decoding the contents of the file.

    Heavily based on
    https://github.com/tomchristie/django-rest-framework/pull/1268

    Updated for Django REST framework 3.
    '''

    def to_internal_value(self, data):
        from django.core.files.base import ContentFile
        import base64
        import six
        import uuid

        # Check if this is a base64 string
        if isinstance(data, six.string_types):
            # Check if the base64 string is in the "data:" format
            if 'data:' in data and ';base64,' in data:
                # Break out the header from the base64 content
                header, data = data.split(';base64,')

            # Try to decode the file. Return validation error if it fails.
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            # Generate file name:
            file_name = str(uuid.uuid4())[:12] # 12 characters are more than enough.
            # Get the file name extension:
            file_extension = self.get_file_extension(file_name, decoded_file)

            complete_file_name = "%s.%s" % (file_name, file_extension, )

            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension

# Serializers define the API representation.
class NetworkDeviceSerializer(FlexFieldsModelSerializer):
    # Upload image using POST data (base64)
    image = Base64ImageField(read_only=False, required=False, allow_null=True)
    # The PuppetMachine object is an optional One-to-One Model Relationship, used when
    # this is a non-generic NetworkDevice, and needs extra fields for Puppet configuration information
    # NOTE: PuppetMachineSerializer here *and* below, to make it show up in the HTTP OPTIONS request, but still make it
    # optional using the FlexFieldsModelSerializer plugin
    puppetmachine = PuppetMachineSerializer(many=False, read_only=False, required=False, allow_null=True)
    # The Webcam object is an optional one-to-one model relationship, used when this NetworkDevice
    # is also one of the IT-managed webcams. See note above about HTTP OPTIONS requests.
    webcam = WebcamSerializer(many=False, read_only=False, required=False, allow_null=True)
    # All Network Interfaces which belong to this NetworkDevice
    networkinterface_set = NetworkInterfaceSerializer(many=True, read_only=False)
    # Synthesized fields
    dnsrecords = DNSRecordSerializer(many=True, source='drf_dnsrecords', read_only=True)
    dhcprecords = DHCPRecordSerializer(many=True, source='drf_dhcprecords', read_only=True)

    class Meta:
        model = NetworkDevice
        # NOTE: must explicitly specify all fields here, rather than using "__all__"
        # so that the FlexFieldsModelSerializer will work it's magic.
        fields = [
            'id',
            'created_at',
            'updated_at',
            'site',
            'image',
            'information',
            'fmxurl',
            'puppetmachine',
            'webcam',
            'networkinterface_set',
            'dnsrecords',
            'dhcprecords',
        ]
        expandable_fields = {
            'site': 'machineconfig.SiteSerializer',
            'puppetmachine': (
                PuppetMachineSerializer,
                {
                    'many': False,
                    'read_only': False,
                    'required': False,
                    'allow_null': True,
                },
            ),
            'webcam': (
                WebcamSerializer,
                {
                    'many': False,
                    'read_only': False,
                    'required': False,
                    'allow_null': True,
                },
            ),
        }

    @mycontext('NetworkDeviceSerializer::validate')
    def validate(self, data):
        print(f'NetworkDeviceSerializer::validate: {data}')
        return data

    @mycontext('NetworkDeviceSerializer::create')
    def create(self, validated_data):
        print(f'NetworkDeviceSerializer::create: CREATE: validated_data={validated_data}')
        # remove sub-objects from validated data
        puppetmachine_data = validated_data.pop('puppetmachine', None)
        webcam_data = validated_data.pop('webcam', None)
        networkinterface_set_data = validated_data.pop('networkinterface_set', [])

        # create new NetworkDevice using validated data
        instance = NetworkDevice.objects.create(**validated_data)

        # create PuppetMachine sub-object
        try:
            if puppetmachine_data is not None:
                serializer = PuppetMachineSerializer(data=puppetmachine_data, context=self.context)
                if not serializer.is_valid():
                    raise serializers.ValidationError(serializer.errors)

                serializer.save(networkdevice=instance)
        except serializers.ValidationError as ex:
            raise serializers.ValidationError({'puppetmachine': ex.detail}) from ex

        # create Webcam sub-object
        try:
            if webcam_data is not None:
                serializer = WebcamSerializer(data=webcam_data, context=self.context)
                if not serializer.is_valid():
                    raise serializers.ValidationError(serializer.errors)

                serializer.save(networkdevice=instance)
        except serializers.ValidationError as ex:
            raise serializers.ValidationError({'webcam': ex.detail}) from ex

        # create NetworkInterface sub-objects
        errors = []
        for interface_data in networkinterface_set_data:
            serializer = NetworkInterfaceSerializer(data=interface_data, context=self.context)
            try:
                if not serializer.is_valid():
                    raise serializers.ValidationError(serializer.errors)

                serializer.save(networkdevice=instance)
                errors.append({})
            except serializers.ValidationError as ex:
                errors.append(ex.detail)

        # handle any errors encountered while validating reverse foreign-key relation
        if any(errors):
            raise serializers.ValidationError({'networkinterface_set': errors})

        # return NetworkDevice instance
        return instance

    @mycontext('NetworkDeviceSerializer::update')
    def update(self, instance, validated_data):
        print(f'NetworkDeviceSerializer::update: UPDATE validated_data={validated_data}')

        # Update fields within PuppetMachine sub-object
        puppetmachine_data = validated_data.pop('puppetmachine', None)
        if puppetmachine_data is not None:
            for attr, value in puppetmachine_data.items():
                setattr(instance.puppetmachine, attr, value)

            if len(puppetmachine_data.items()) > 0:
                try:
                    instance.puppetmachine.save()
                except serializers.ValidationError as ex:
                    raise serializers.ValidationError({'puppetmachine': ex.detail})

        # Update fields within Webcam sub-object
        webcam_data = validated_data.pop('webcam', None)
        if webcam_data is not None:
            for attr, value in webcam_data.items():
                setattr(instance.webcam, attr, value)

            if len(webcam_data.items()) > 0:
                try:
                    instance.webcam.save()
                except serializers.ValidationError as ex:
                    raise serializers.ValidationError({'webcam': ex.detail})

        # Our DB transaction is locked thanks to perform_update(), so we don't have anything
        # to worry about in that regard. Now we need to avoid the DB from crashing because
        # our NetworkInterface sub-objects must have UNIQUE MAC Address fields.
        #
        # So we DELETE our NetworkInterface sub-objects (within the DB transaction) so
        # that the database uniqueness validation will work. :-)
        instance.networkinterface_set.all().delete()

        # And now we go through and create all of the objects again. Note that you MUST pop
        # the sub-object's validated data before creating the current object.
        networkinterface_set_data = validated_data.pop('networkinterface_set', [])

        # create all of the NetworkInterface sub-objects again, since they were DELETE-ed up above
        errors = []
        for interface_data in networkinterface_set_data:
            serializer = NetworkInterfaceSerializer(data=interface_data, context=self.context)
            try:
                if not serializer.is_valid():
                    raise serializers.ValidationError(serializer.errors)

                serializer.save(networkdevice=instance)
                errors.append({})
            except serializers.ValidationError as ex:
                errors.append(ex.detail)

        # handle any errors encountered while validating reverse foreign-key relation
        if any(errors):
            raise serializers.ValidationError({'networkinterface_set': errors})

        # Now set the updated field values (normal fields, rather than nested ForeignKey relationships)
        for attr, value in validated_data.items():
            # We are about to update the NetworkDevice.image field, so we should delete
            # the previous image from the AWS S3 storage now. This has the potential of
            # leaving inconsistent data if the image delete succeeds, but the reliability
            # requirements of this application don't need this level of concern. We're more
            # concerned with the storage costs.
            if attr == 'image' and instance.image is not None:
                instance.image.delete(save=False)

            setattr(instance, attr, value)

        # Save the record and return to the user
        instance.save()
        return instance

class SiteDashboardDataSerializer(serializers.Serializer):
    '''
    A Serializer for some manually-generated data for the Global Activite Dashboard
    '''
    unrecognized_device_count = serializers.IntegerField(read_only=True)
    boot_mode_local_count = serializers.IntegerField(read_only=True)
    boot_mode_rebuild_count = serializers.IntegerField(read_only=True)
    boot_mode_rebuildalt_count = serializers.IntegerField(read_only=True)
    boot_mode_rescue_count = serializers.IntegerField(read_only=True)

# Serializers define the API representation.
class SiteSerializer(FlexFieldsModelSerializer):
    '''
    A Serializer (API Representation) of a Site which is used for the
    "retrieve" Django REST Framework API action. This is what you get
    when you HTTP GET a specific object out of the API.
    '''
    # Synthesized Fields
    device_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Site
        fields = '__all__'
        expandable_fields = {
            # Optional list of devices at this Site
            'devices': (
                'machineconfig.NetworkDeviceSerializer',
                {
                    'source': 'networkdevice_set',
                    'many': True,
                    'read_only': True,
                    'expand': [
                        'puppetmachine',
                    ],
                    'omit': [
                        'puppetmachine.facts',
                        'puppetmachine.lcogtinstruments',
                    ],
                },
            ),
            # Optional list of DNS records at this Site
            'dnsrecords': (
                'machineconfig.DNSRecordSerializer',
                {
                    'source': 'drf_dnsrecords',
                    'many': True,
                    'read_only': True,
                },
            ),
            # Optional list of DHCP records at this Site
            'dhcprecords': (
                'machineconfig.DHCPRecordSerializer',
                {
                    'source': 'drf_dhcprecords',
                    'many': True,
                    'read_only': True,
                },
            ),
            # Optional list of unrecognized devices at this Site
            'unrecognized_devices': (
                'machineconfig.UnrecognizedPXEDeviceSerializer',
                {
                    'source': 'drf_unrecognized_devices',
                    'many': True,
                    'read_only': True,
                    'expand': [
                        'site',
                    ],
                    'omit': [
                        'site',
                    ],
                },
            ),
            # Optional (read-only) Site Dashboard Data
            'dashboard_data': (
                'machineconfig.SiteDashboardDataSerializer',
                {
                    'source': 'drf_dashboard_data',
                    'read_only': True,
                },
            ),
        }

    @mycontext('SiteSerializer::validate')
    def validate(self, data):
        print(f'SiteSerializer::validate: {data}')
        return data

    @mycontext('SiteSerializer::create')
    def create(self, validated_data):
        print(f'SiteSerializer::create: CREATE')
        return super().create(validated_data=validated_data)

    @mycontext('SiteSerializer::update')
    def update(self, instance, validated_data):
        print(f'SiteSerializer::update: UPDATE')
        # Our DB transaction is locked thanks to perform_update(), so we don't have anything
        # to worry about in that regard. We need to remove and then re-create our NTP Servers
        # each time we update the Site. This makes the nested sub-objects thing work correctly.
        instance.ntpserver_set.all().delete()
        # Call into the normal update path
        return super().update(instance=instance, validated_data=validated_data)

class UnrecognizedPXEDeviceSerializer(FlexFieldsModelSerializer):
    site = SiteSerializer(read_only=True)
    found = serializers.BooleanField(read_only=True)
    networkdevice_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = UnrecognizedPXEDevice
        fields = '__all__'
        expandable_fields = {
            'site': (
                'machineconfig.SiteSerializer',
                {
                    'read_only': True,
                }
            ),
        }

# vim: set ts=4 sts=4 sw=4 et tw=120:
